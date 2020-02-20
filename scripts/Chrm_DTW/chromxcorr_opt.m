function r = chromxcorr_opt(A, F, L)
% r = chromxcorr(A,F,L)
%   Cross-correlate two chroma ftr vecs in both time and
%   transposition
%   Both A and F can be long, result is full convolution
%   (length(A) + length(F) - 1 columns, in F order).
%   L is the maximum lag to search to - default 100.
%   of shorter, 2 = by length of longer
%   Optimized version.
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
% STP's optimized version - read scaled ffts rather than chromagrams; do the whole job in 1 IFFT
%   also assumes we're using 1 minute max.
%

if nargin < 3;  L = 800; end

nchr = 12;

r = zeros(nchr, 2 * L + 1);

%for i = 1:nchr
%  rr = 0;
%  for j = 1:nchr
%    rr = rr + xcorr(F(1+rem(j+i-2,nchr),:),A(j,:),L);
%  end
%  r(i,:) = rr;
%end

% super speed up by Jesper hoevang jensen jhj@es.aau.dk 2007-05-04
% execution time of 80x80 comparison on macbook pro goes from 3700s 
% to 336s!!!  (only 891s to 418s on hog)

beats = max(length(A), length(F));
%beats = 2000;
t = beats + 2 * L + 1;

disp(['    chromxcorr_opt: ', num2str(length(A)), ' - ', num2str(length(F)), ' - ', num2str(t)]);
%    chromxcorr: 852 - 1591 - 3192
%    chromxcorr: 2708 - 1591 - 4309

t2 = ifft2(F .* A);     %%%% stp's super-simplified version %%%%

r = [t2(:, end - L + 1 : end) t2(:, 1 : L + 1)];

% Normalize by shorter vector so max poss val is 1

r = r / beats;
