%% Script to run a song through the LABROSA Beat-synched-chroma - DTW cover song detection package% Run this with:%   octave RunOneSong.m ../../../covers80_32k/aiff/annie_lennox+Medusa+02-Take_Me_To_The_River.aiff% Called from python code as,% octave -p ./scripts/Chrm_DTW  ./scripts/Chrm_DTW/RunOneSong.m  ./scripts/Chrm_DTW/list_stp.txt  ./scripts/Chrm_DTW/ChrmGrms0/  /Users/stp/Code/CoSoDe/covers80_32k/aiff/annie_lennox+Medusa+02-Take_Me_To_The_River.aiffpkg load signal;% Defaultssrcext = ''; dstext = '.chrm'; skip = 0; fctr = 400;     % downweight fundamentals below herefsd = 1.0; ctype = 1; audio_dir = '/Content/Code/SndsLike/CoSoDe/covers80_32k/aiff';arg_list = argv();%disp(['Got ', num2str(length(arg_list)), ' args'])if length(arg_list) < 3  f_list_fil = 'list_stp.txt';  chgrm_dir = 'ChrmGrms0/';  ifname = arg_list{1};else  f_list_fil = arg_list{1};;  chgrm_dir = arg_list{2};  ifname = arg_list{3};enddo_parallel = false;      % run in many threads (Linux-only)take1 = false;            % take 1 minute from the middle of the songpre_proc = false;         % do the pre-processing power/norm/FFT before the saven_ret = 20;               % # of return values##printf("%s", program_name());##for i = 1:nargin##    printf(" %s", arg_list{i});##end##printf("\n");%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% LOAD DB %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%nowd = datestr(rem(now, 1), 'HH:MM:SS');disp('')disp(['    -------- Load song database at ', nowd, ' --------']);disp('')[files, nfiles] = listfileread(f_list_fil);if nfiles < 1  error(['No sound file names read from list file "', f_list_fil, '"']);endif do_parallel                             % do analysis in parallel threads (Linux-only)  opfiles = pararrayfun(12, @do_analyze_file, files, audio_dir, '', chgrm_dir, 0, 400, 1.0, 1, take1, pre_proc);else                                       %%%%%%%%%%%%%%%% calclistftrs  opfiles = calclistftrs(f_list_fil, audio_dir, '', chgrm_dir, '.chrm', 0, 400, 1.0, 1, take1, pre_proc);end% disp(opfiles);%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ANALYSIS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%nowd = datestr(rem(now, 1), 'HH:MM:SS');disp('')disp(['    -------- Starting analysis at ', nowd, ' --------']);disp('')% Calculate and store the beat-synchronous chroma features for the input file                                            %%%%%%%%%%%%%%%% do_analysis[chgrm, fnam] = do_analysis(ifname, audio_dir, srcext, chgrm_dir, dstext, skip, fctr, fsd, ctype, take1, pre_proc);tlist{1} = fnam;%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% MATCHING %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%nowd = datestr(rem(now, 1), 'HH:MM:SS');disp('')disp(['    -------- Starting matching at ', nowd, ' - ', num2str(length(opfiles)), ' candidate(s) --------']);disp('')%[R, S, T, C] = do_match(opfiles, chgrm, take1, pre_proc);    %%%%%%%%%%%%%%%% do_match[R, S, T, C] = coverTestLists(opfiles, tlist, 0.5, 2, 0, take1, pre_proc);  %[R, S, T, C] = coverTestLists(tlist, opfiles, 0.5, 2, 0, take1, pre_proc);  R = abs(R);             % abs valR = R .* R * 100000;    % square and scale result                        % save matches to a CSV filecsvnam = ['Results_', datestr(now, 'yy_mm_dd_HH_MM'), '.csv'];dlmwrite(csvnam, R, '\t', "precision", 3)##disp('R')##disp(R);##disp('S')##disp(S);##disp('T')##disp(T);##disp('C')##disp(C);vals = [];inds = [];for in = 1 : n_ret  [x, ix] = max(R);  vals(in) = x;  inds(in) = ix;  R(ix) = 0;end##disp('vals')##disp(vals);##disp('inds')##disp(inds);disp('--Results--')for in = 1 : n_ret  disp([num2str(inds(in)), ' | ', num2str(vals(in)), ' | ', files(inds(in)){1}]);enddisp('--End--')