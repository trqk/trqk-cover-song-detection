function opfiles = calclistftrs(listfile, srcprepend, srcext, dstprepend, dstext, skip, fctr, fsd, ctype, take1, pre_proc)
% calclistftrs(listfile,srcprepend,srcext,dstprepend,dstext,fctr,fsd,ctype)
%   Take listile, a list of input MP3 or WAV files and calculate 
%   beat-synchronous chroma features for each one. 
%   input file names each have srcprepend prepended and srcext appended;
%   features are written to .mat files with the same root name but
%   with dstprepend prepended and dstext appended.  First <skip>
%   items are skipped (for resumption of interrupted runs).
%   fctr and fsd specify a spectral window used to extract chroma 
%   elements with center at fctr Hz, and gaussian log-F half-width
%   of fsd octaves.
%   Return a cell array of the output files written.
% 2006-07-14 dpwe@ee.columbia.edu

%   Copyright (c) 2006 Columbia University.
% 
%   This file is part of LabROSA-coversongID
% 
%   LabROSA-coversongID is free software; you can redistribute it and/or modify
%   it under the terms of the GNU General Public License version 2 as
%   published by the Free Software Foundation.
% 
%   LabROSA-coversongID is distributed in the hope that it will be useful, but
%   WITHOUT ANY WARRANTY; without even the implied warranty of
%   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
%   General Public License for more details.
% 
%   You should have received a copy of the GNU General Public License
%   along with LabROSA-coversongID; if not, write to the Free Software
%   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
%   02110-1301 USA
% 
%   See the file "COPYING" for the text of the license.

%
% STP's optimized version - use 1 minute around the center of the recording and do scaling & fft before storing
%

if nargin < 2; srcprepend = ''; end
if nargin < 3; srcext = ''; end
if nargin < 4; dstprepend = ''; end
if nargin < 5; dstext = '.chrm'; end
if nargin < 6; skip = 0; end
if nargin < 7; fctr = 400; end        % downweight fundamentals below here
if nargin < 8; fsd = 1.0; end
if nargin < 9; ctype = 1; end

[files, nfiles] = listfileread(listfile);

if nfiles < 1
  error(['No sound file names read from list file "',listfile,'"']);
end

opfiles{nfiles} = '';       % preallocate array to placate mlint

for songn = 1 : nfiles
  tline = files{songn};

  if length(srcext) > 0
    if tline(end - length(srcext) + 1 : end) == srcext
      % chop off srcext already there
      tline = tline(1 : end - length(srcext));
    end
  else
    % no srcext specified - must be part of input file name
    % separate name and extension for input file
    [srcpath, srcname, srcext] = fileparts(tline);
    tline = fullfile(srcpath, srcname);
  end
 
  % lines are 
  ifname = fullfile(srcprepend, [tline, srcext]);
  ofname = fullfile(dstprepend, [tline, dstext]);
  
  if exist (ofname, "file")     # if the file exists, read it...
    fnd = 1;
%    disp(['Song ', num2str(songn), ' - ', ofname, ' - ChrmGrm file found']);
  elseif songn > skip
    disp(['Song ', num2str(songn), ' = ', tline]);
    ofdir = fileparts(ofname);
    % Make sure the parent directory exists
    mymkdir(ofdir)

    % wav/aiff files or mp3 files
    if strcmp(srcext,'.mp3')
      [d, sr] = mp3read(ifname, 'size');
      if sr >= 32000
        ds = 2;
      else
        ds = 1;
      end
      [d, sr] = mp3read(ifname, 0, 1, ds); 
    elseif strcmp(srcext, '.wav')
      [d,sr] = wavread(ifname);         % wav - use wavread
    else
      [d, sr] = audioread(ifname);      % aiff - use audioread
    end

    if take1                  %%%% take the middle minute of the songs
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
                %%%% do the analysis %%%%%%%%%
    [F, bts] = chrombeatftrs(d, sr, fctr, fsd, ctype);
    
    if pre_proc               %%%% sqrt, normalize, fft before save
      pwr = 0.5;
      F = chromnorm(chrompwr(F, pwr));
      L = 800;
%      beats = length(F);
      beats = 2000;
      t = beats + 2 * L + 1;
      nchr = 12;
      F = fft2(F, nchr, t);
      F = conj(F);
    end
                %%%% save the results
    save(ofname, 'ifname', 'F', 'bts');
    
%   disp([datestr(rem(now,1),'    HH:MM:SS'), ' ', ifname,' ncols=', num2str(size(F,2)),
%      ' bpm=', num2str(60/median(diff(bts)))]);

    disp([datestr(rem(now,1),'    HH:MM:SS'), ' - nbeats = ', num2str(size(F, 2))]);
  end
  opfiles{songn} = ofname;
end
