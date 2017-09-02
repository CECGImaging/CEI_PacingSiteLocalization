%% SCRIPT TO RUN THE CECGI experiments 
% All these methods can be found at:
%
%	https://github.com/jcollfont/inverseecg


clc;clear all; close all;

addpath(genpath('~/Documents/Research/ECG/inverseECG/'));
run('~/links/activationTimes/addpaths_activationTimes.m');

%% PARAM
	% path to datasets
	sourceModelPaths = {'~/Desktop/PacingDataset/Epiout/',...
						'~/Desktop/PacingDataset/EndoEpiout/',...
						'~/Desktop/PacingDataset/EndEpiTMPout/'};

	% inverse methods to run
	inverseMethod = {'tikh0','tikh1','tikh2','spline','messnarz'};%,'TSVD','greensite','TV'};

%% for all the sourceModels
for srcModel = 1:numel(sourceModelPaths)
	
	% load files
	files = dir([sourceModelPaths{srcModel}, 'TestData/']);
	
	% load fwd matrix and geometry
	for fi = 3:numel(files)
		
		if strfind(files(fi).name,'lfmatrix')
			load([sourceModelPaths{srcModel}, 'TestData/', files(fi).name]);
			if exist('EP_LFmatrix')
				A = EP_LFmatrix;
			elseif exist('TMV_LFmatrix')
				A = TMV_LFmatrix;
			end
			
			[N,M] = size(A);
			
		elseif numel(strfind(files(fi).name,'surf_endoepi')) + numel(strfind(files(fi).name,'surf_peri')) > 0
			load([sourceModelPaths{srcModel}, 'TestData/', files(fi).name]);
			heart = scirunfield;
			
			% compute geometry regularization matrices
				% compute adjacency matrix
				pathLength = 3;
				[AdjMtrx] = computeAdjacencyMatrix(heart, pathLength);

				% compute gradient estimator
				wghFcn = @(indx) AdjMtrx(indx,:);
				[D, H] = meshVolDiffHessMatrix(heart,wghFcn);	
				Lapl = LaplacianMatrixFromHessianMatrix(H);

				% regularize reg matrices
				Rd = D'*D + 1e-3*eye(M);
				Lapl = Lapl + 1e-3*eye(M);
		end
	end
	
	%% for all files in the dataset
	for fi = 1:numel(files)
		
		parsedName = strsplit(files(fi).name,'_');
		
		if strfind(files(fi).name,'BSP')
			
			% load file
			load([sourceModelPaths{srcModel}, 'TestData/', files(fi).name]);
			ECG = BSP.potvals;
			
			for invM = 1:numel(inverseMethod)
				
				% skip messnarz if the source model is not based on TMPs
				if (srcModel ~= 3)&&(invM == 5)
					invM = 6;
				end
				%% select method
				switch inverseMethod{invM}

					case 'tikh0'	% Run Tikhonov 0th order
						vec_lambda = 10.^linspace(-8,-3,1000);
						[EGM_sol] = tikhonov_jcf(A, eye(M), eye(N), ECG, vec_lambda, false);

					case 'tikh1'	% Run Tikhonov 1st order
						vec_lambda = 10.^linspace(-6,-3,1000);
						[EGM_sol] = tikhonov_jcf(A, Rd, eye(N), ECG, vec_lambda, false);

					case 'tikh2'	% Run Tikhonov 2nd order
						vec_lambda = 10.^linspace(-6,-3,1000);
						[EGM_sol] = tikhonov_jcf(A, Lapl, eye(N), ECG, vec_lambda, false);

					case 'TSVD'		% Run TSVD

					case 'greensite'% Run Isotropy method

					case 'spline'	% Run Spline-inverse
						vec_lambda = 10.^linspace(-6,-3,1000);
						[EGM_sol] = splineInverse(A, ECG, Rd, vec_lambda, false);
						
					case 'messnarz'	% run messnarz (if valid assumption)
						vec_lambda = 10.^linspace(-6,-3,50);
						[EGM_sol] = inverse_messnarz_ADMM(ECG, A, eye(M), vec_lambda, [-85 30], {10, 1e-3, 1e-3});
						
					case 'TV'		% run Total variation
						

				end % switch

				%% run activation times and  detect PVC location
				if srcModel == 3
					[acttimes] = activationTimes_wrapper( -EGM_sol,D,[] );
				else
					[acttimes] = activationTimes_wrapper( EGM_sol,D,[] );
				end
					[~,ix] = min(acttimes);
					pacLoc = heart.node(:,ix);
					

				%% save results
					% potentials
					saveName = [sourceModelPaths{srcModel}, 'solutions/', inverseMethod{invM}, '/CEIPVC2017_1_',parsedName{end}(1:end-4),'_POT_jcollfont',inverseMethod{invM},'_.mat' ];
					save(saveName, 'EGM_sol');
				
					% activation times
					saveName = [sourceModelPaths{srcModel}, 'solutions/', inverseMethod{invM}, '/CEIPVC2017_1_',parsedName{end}(1:end-4),'_AT_jcollfont',inverseMethod{invM},'_.mat' ];
					save(saveName, 'acttimes');
					
					% PVC localization
					saveName = [sourceModelPaths{srcModel}, 'solutions/', inverseMethod{invM}, '/CEIPVC2017_1_',parsedName{end}(1:end-4),'_LOC_jcollfont',inverseMethod{invM},'_.mat' ];
					save(saveName, 'pacLoc');
				
			end % inverse methods
		end % if 
	end % files
end % source models
	
	
	
	
	

	
	
	
	