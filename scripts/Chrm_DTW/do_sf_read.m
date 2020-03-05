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
else
  [d, sr] = audioread(ifname);      % aiff/wav - use audioread
end

if ndims(d) == 2                    % sum to mono
  d = sum(d, 2) / size(d, 2);
endif
