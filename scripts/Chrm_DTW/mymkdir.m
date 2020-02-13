function r = mymkdir(dir)
% r = mymkdir(dir)
%   Ensure that dir exists by creating all its parents as needed.
% 2006-08-06 dpwe@ee.columbia.edu

[x,m,i] = fileattrib(dir);
%disp(['Check ', '"', dir, '"']);
if strcmp(dir, '') 
  return
endif
if x == 0
  [pdir,nn,ee] = fileparts(dir);
  mymkdir(pdir);
  disp(['creating ',dir,' ...']);
  mkdir(pdir, nn);
end
