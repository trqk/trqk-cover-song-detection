function [R, S, T, C] = do_match(chgrm, flist, take1, pre_proc)
% [R, S, T, C] = do_match(chgrm, ntlist)
% Run the matching phase

pkg load signal;

##pre_proc = false;   % do the pre-processing power/norm/FFT/conj before the save
maxlag = 800;         % max lag is 800 windows
metric = 2; 

                  % file loop over data set chgrm files
for i = 1 : length(flist)
  P = load(flist{i});
                  %%%%%% Perform the cross-correlation of the two chroma beat ftr matrices %%%%%%%
  if pre_proc
    r = chromxcorr_opt(chgrm.F, P.F, maxlag);
  else
    r = chromxcorr(chgrm, P.F, maxlag);
  end
                  % find best alignments
  mmr = max(max(r));
  bestchrom = find(max(r, [], 2) == mmr);
  
  if metric == 1          % 1 = peak xcorr
    R(i) = mmr;
    besttime = find(max(r) == mmr);
    S(i) = mean(mean(r( :, max(besttime - 100, 1) : min(besttime + 100, size(r, 2)))));
    
  elseif metric == 2      % 2 = peak filtered xcorr, dflt
                          % Look for rapid variation - do HPF along time of best chrom
    fxc = filter([1 -1], [1 -.9], r(bestchrom, :) - mean(r(bestchrom, :)));
                          % chop off first bit - onset transient for start-in-the-middle
    fxc(1 : 50) = min(fxc);
    R(i) = max(fxc);
    refpt = maxlag;
  end
  
  besttime = find(fxc == max(fxc)) - refpt - 1;
  T(i) = besttime;
  C(i) = bestchrom;
  S(i) = sqrt(mean(fxc(max(besttime + refpt - 100, 1) : min(besttime + refpt + 100, length(fxc))) .^ 2));
end
