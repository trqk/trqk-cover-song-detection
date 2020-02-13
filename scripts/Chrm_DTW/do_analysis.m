function [chgrm, ofname] = do_analysis(infile, srcprepend, srcext, dstprepend, dstext, skip, fctr, fsd, ctype, take1, pre_proc)
% do_analysis(infile,srcprepend,srcext,dstprepend,dstext,fctr,fsd,ctype)
% Run a song through the LABROSA Beat-synched-chroma - DTW cover song detection package
%   See comment in calclistftrs.m

pkg load signal;

% Defaults

if nargin < 2; srcprepend = ''; end
if nargin < 3; srcext = ''; end
if nargin < 4; dstprepend = ''; end
if nargin < 5; dstext = '.chrm'; end
if nargin < 6; skip = 0; end
if nargin < 7; fctr = 400; end      % downweight fundamentals below here
if nargin < 8; fsd = 1.0; end
if nargin < 9; ctype = 1; end

##take1 = false;        % take 1 minute from the middle of the song
##pre_proc = false;     % do the pre-processing power/norm/FFT before the save

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ANALYSIS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Calculate and store the beat-synchronous chroma features for the input file

[srcpath, srcname, srcext] = fileparts(infile);
if infile(1) != '/'
  ifname = fullfile(srcprepend, [infile, srcext]);
else
  ifname = infile
end

ofname = fullfile(dstprepend, [srcname, dstext]);

##if exist(ofname, "file")     # if the file exists, read it...
##  chgrm = load(ofname);
##  disp(['    Song "', ofname, '" -- ChrmGrm file found']);
##  return
##end

disp(['Song = ', srcname]);        % Print song name

ofdir = fileparts(ofname);
mymkdir(ofdir)      % Make sure the parent directory exists

[d, sr] = do_sf_read(infile, srcext);    % read sound file
%disp(['  -- Len: ', num2str(length(d)), ' - SR: ', num2str(sr)]);

if take1        # take1 = take the middle minute of the song
  samplen = 60;
  dur = length(d) / sr;
  if dur > samplen
%        disp(['      -- Len: ', num2str(length(d)), ' - SR: ', num2str(sr)]);
    midpt = round(dur / 2 * sr);
    rng = round(samplen / 2 * sr);
%        disp(['      -- Subset: ', num2str(dur, "%.1f"), ' : ', num2str(midpt - rng), ' - ', num2str(midpt + rng)]);
    d = d(midpt - rng : midpt + rng);    % subset of samples around mid-point
%        disp(['Len: ', num2str(length(d))]);
  end
end
            %%%%%%%%%%%%%% do the analysis %%%%%%%%%
[F, bts] = chrombeatftrs(d, sr, fctr, fsd, ctype);

if pre_proc     % pre_proc = sqrt, normalize, fft before save
  pwr = 0.5;
  F = chromnorm(chrompwr(F, pwr));
  L = 800;
  beats = length(F);
  if take1 > 0
    beats = 2000;
  end
  t = beats + 2 * L + 1;
  nchr = 12;
  F = fft2(F, nchr, t);
  F = conj(F);
end
            %%%% save the results
save(ofname, 'ifname', 'F', 'bts');

%   disp([datestr(rem(now,1),'    HH:MM:SS'), ' ', ifname,' ncols=', num2str(size(F,2)),
%      ' bpm=', num2str(60/median(diff(bts)))]);

                  % Print results
%disp([datestr(rem(now,1),'    HH:MM:SS'), ' - nbeats = ', num2str(size(F, 2))]);

chgrm = F;     % return result
