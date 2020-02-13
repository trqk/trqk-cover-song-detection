function [d, sr] = do_sf_read(ifname, srcext)
% [d, sr] = do_sf_read(infile, srcext)
% Read mp3/wav/aiff files

pkg load signal;

if strcmp(srcext, '.mp3')
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
