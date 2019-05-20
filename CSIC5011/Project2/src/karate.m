clear;
clc;
load karate.mat

D = sum(A, 2);
N = length(D);
TransProb = diag(1./D) * A;     % Transition matrix of the Markov chain
LMat = TransProb - diag(ones(N, 1));    % Laplacian matrix

% source set A contains the coach
% target set B contains the president 
SetA = 1; % [44:54];%[find(ind==19)];%[44:54];%18 + 1;
SetB = 34; %[find(ind==11)];%10 + 1; % seems to be 11 instead of 10

% find the equilibrium distribution
[EigV, EigD] = eig(LMat');
EquiMeasure = EigV(:, 1)./sign(EigV(1,1));
figure;
bar(EquiMeasure);

% find the Cheeger vector
nLMat = sqrt(diag(1./D)) * (diag(D)-A) * sqrt(diag(1./D));
[nEigV, nEigD] = eig(nLMat);
CheegerVector = nEigV(:, 2)./sign(nEigV(1,2));
CheegerVector = double(CheegerVector < 0);
figure;
plot((CheegerVector-c0),'ko','MarkerEdgeColor','k','MarkerFaceColor','k','MarkerSize',10);

% determine the local minimum
for i = 1:N
  localmin = true;
  for j = setdiff(1:N, i)
    if ((LMat(i,j)>0)&(EquiMeasure(j)>EquiMeasure(i))) 
      localmin = false;
      break
    end
  end
  if (localmin)
    i
  end
end

TransLMat = diag(EquiMeasure) * LMat * diag(1./EquiMeasure); 

SourceSet = SetA;
TargetSet = SetB;
RemainSet = setdiff(1:N, union(SourceSet, TargetSet));

% Initialization of Committor function: transition probability of reaching
% the target set before returning to the source set.
CommitAB = zeros(N, 1);
CommitAB(SourceSet) = zeros(size(SourceSet));
CommitAB(TargetSet) = ones(size(TargetSet));

LMatRestrict = LMat(RemainSet, RemainSet);
RightHandSide = - LMat(RemainSet, TargetSet) * CommitAB(TargetSet);

% Solve the Dirchelet Boundary problem
CommitAB(RemainSet) = LMatRestrict \ RightHandSide;

% Clustering into two basins according to the transition probability 
ClusterA = find(CommitAB <= 0.5);
ClusterB = find(CommitAB > 0.5);
ClusterAB = -1*ones(N,1);  ClusterAB(ClusterA) = 0; ClusterAB(ClusterB) = 1;     
if nnz(ClusterAB==-1)~=0 || ~isempty(intersect(ClusterA,ClusterB)), 
    error('Wrong clustering!'); 
end

% Show the difference between decompositions 
figure;
plot((ClusterAB-c0),'ko','MarkerEdgeColor','k','MarkerFaceColor','k','MarkerSize',10);
set(gca,'YTick',[0 1]);  xlabel('Node','fontsize',12);

% The inverse transition probability
CommitBA = zeros(N, 1);
CommitBA(SourceSet) = ones(size(SourceSet));
CommitBA(TargetSet) = zeros(size(TargetSet));

LMatRestrict = LMat(RemainSet, RemainSet);
RightHandSide = - LMat(RemainSet, SourceSet) * CommitBA(SourceSet);

% Dirichelet Boundary Problem with inverse transition probability
CommitBA(RemainSet) = LMatRestrict \ RightHandSide;

RhoAB = EquiMeasure .* CommitAB .* CommitBA;
%}

% Current or Flux on edges (reactive current?)
CurrentAB = diag(EquiMeasure .* CommitBA) * LMat * diag(CommitAB);
CurrentAB = CurrentAB - diag(diag(CurrentAB));

% Effective Current Flux
EffCurrentAB = max(CurrentAB - CurrentAB', 0);

% Transition Current or Flux on each node
TransCurrent = zeros(N, 1); 
TransCurrent(ClusterA) = sum(EffCurrentAB(ClusterA, ClusterB), 2);
TransCurrent(ClusterB) = sum(EffCurrentAB(ClusterA, ClusterB), 1);

% figure of the fission
Grap = graph(A);
figure;
plotTruth = plot(Grap,'Marker', 'o', 'MarkerSize',10,'Layout','force','EdgeColor', 'black'); 
axis off;
for i = 1:N
    highlight(plotTruth,i,'NodeColor',[1-ClusterAB(i) 0 ClusterAB(i)]);
end
highlight(plotTruth, SetA,'Marker', 'p', 'MarkerSize', 20);
highlight(plotTruth, SetB,'Marker', 'p', 'MarkerSize', 20);
nl = plotTruth.NodeLabel;
plotTruth.NodeLabel = '';
xd = get(plotTruth, 'XData');
yd = get(plotTruth, 'YData');
text(xd, yd, nl, 'FontSize',8, 'FontWeight','bold', 'HorizontalAlignment','left', 'VerticalAlignment','middle');



% figure of the result
DGrap = digraph(EffCurrentAB);
figure;
plotResul = plot(DGrap,'Marker', 'o', 'MarkerSize', 10, 'Layout', 'force','EdgeColor', 'black');
nl = plotResul.NodeLabel;
plotResul.NodeLabel = '';
xd = get(plotResul, 'XData');
yd = get(plotResul, 'YData');
text(xd, yd, nl, 'FontSize',12, 'FontWeight','bold', 'HorizontalAlignment','left', 'VerticalAlignment','middle');
axis off;


mmax = max(TransCurrent);
lmax = max(max(EffCurrentAB));
for i = 1:N
    % thresholding scheme based on the committor function
    if CommitAB(i)<.5
        highlight(plotResul,i,'NodeColor',[1-CommitAB(i) 0 0]);
    else
        highlight(plotResul,i,'NodeColor',[0 0 CommitAB(i)]);
    end
    % Transition current (proportional to the node size)    
    highlight(plotResul,i,'MarkerSize',round(10+32*TransCurrent(i)/mmax));
    % Effect current current (proportional to the edge size) 
    for j = 1:N
        if EffCurrentAB(i,j)~=0
            highlight(plotResul,i,j,'Linewidth',round(1+4*EffCurrentAB(i,j)/lmax), 'EdgeColor', 'black');
        end
    end
end
highlight(plotResul, SetA,'Marker', 'p', 'MarkerSize', round(10+32*TransCurrent(SetA)/mmax));
highlight(plotResul, SetB,'Marker', 'p', 'MarkerSize', round(10+32*TransCurrent(SetB)/mmax));
    