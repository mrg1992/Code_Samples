function igt_mri(contact, sid, save_path)
IOPort('CloseAll');
triger_config = 'BaudRate=4800 StopBits=0 Parity=None DataBits=8';
resp_config = 'BaudRate=9600 StopBits=0 Parity=None DataBits=8';
[triger_handle, errmsg] = IOPort('OpenSerialPort', 'COM1', triger_config);
[resp_handle, errmsg] = IOPort('OpenSerialPort', 'COM4', resp_config);
[wPtr, wRect, old_pref] = init_screen();
i = 0;
decks = penalty_dist(40); % 40 card in each deck
acc_reward = 0;
acc_punish = 0;
max_itr = 101;
game_seq = zeros(3,max_itr); % sequence of card selection
resp_times = zeros(max_itr,6);
wait_for_triger(triger_handle);
shuffle_decks = randperm(4);
show_decks(wPtr, decks, shuffle_decks, 0);
itr = 1;
time_base = tic;
while itr < max_itr % iteration of card selection by subject
%============================
is_deck_selected = 0;
show_decks(wPtr, decks, shuffle_decks, 0);
resp_timer = tic;
[selected_deck, resp_time] = read_response_box(wPtr, resp_handle, resp_timer);
selected_deck = 5 - selected_deck; % complement selection
current_reward = 0;
current_punish = 0;
orig_sel = selected_deck;
selected_deck = shuffle_decks(selected_deck);39
ind = selected_deck;
if selected_deck == 'a' || selected_deck == 'A' || selected_deck == '1'|| selected_deck == 1
if (decks.index(1,ind) <= 40)
is_deck_selected = 1;
end
end
if selected_deck == 'b' || selected_deck == 'B' || selected_deck == '2' || selected_deck == 2
if (decks.index(1,ind) <= 40)
is_deck_selected = 1;
end
end
if selected_deck == 'c' || selected_deck == 'C' || selected_deck == '3' || selected_deck == 3
if (decks.index(1,ind) <= 40)
is_deck_selected = 1;
end
end
if selected_deck == 'd' || selected_deck == 'D' || selected_deck == '4' || selected_deck == 4
if (decks.index(1,ind) <= 40)
is_deck_selected = 1;
end
end
if is_deck_selected
current_reward = decks.reward(ind ,decks.index(1, ind));
current_punish = decks.punish(ind ,decks.index(1, ind));
decks.index(1, ind) = decks.index(1, ind) + 1;
resp_times(itr,:) = resp_time;
game_seq(:,itr) = [selected_deck; current_reward; current_punish];
itr = itr + 1;
show_msg(wPtr, current_reward, current_punish, orig_sel);
acc_reward = acc_reward + current_reward;
acc_punish = acc_punish + current_punish;
end
% ==== rest
show_decks(wPtr, decks, shuffle_decks, 1);
tic
while toc < 8
end
end
finished_him(wPtr);
quit(old_pref);
data_file = sprintf('%s/%d.dat', save_path, sid);
time_base = toc(time_base);
save(data_file, 'game_seq', 'contact', 'time_base', 'resp_times');
end40
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function finished_him(wPtr)
white = WhiteIndex(wPtr); % pixel value for white
black = BlackIndex(wPtr); % pixel value for black
gray = (white + black) / 2;
screen_size = Screen('Resolution', 0);
w_space = screen_size.width / 2;
h_space = screen_size.height / 3;
offset = 40;
offset_w = 120;
text_h = h_space * 1.5;
text_w = w_space;
Screen('TextFont', wPtr, char('Helvetica'));
Screen('TextStyle', wPtr, 1);
Screen('TextSize', wPtr, 30);
Screen('DrawText', wPtr, sprintf('Game has been Finished'), text_w - offset_w, text_h + 80, black, gray);
rect = [(screen_size.width / 2) (screen_size.height / 2) (screen_size.width / 2 + 20) (screen_size.height / 2 + 20)];
Screen('FillOval', wPtr, [0,0,0], rect);
Screen(wPtr, 'Flip', [], 1);
system('killall ffmpeg');
Screen('FillOval', wPtr, gray, rect);
Screen(wPtr, 'Flip');
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function wait_for_start(wPtr)
white = WhiteIndex(wPtr); % pixel value for white
black = BlackIndex(wPtr); % pixel value for black
gray = (white + black) / 2;
screen_size = Screen('Resolution', 0);
w_space = screen_size.width / 2;
h_space = screen_size.height / 3;
offset = 40;
offset_w = 120;
text_h = h_space * 1.5;
text_w = w_space;
Screen('TextFont', wPtr, char('Helvetica'));
Screen('TextStyle', wPtr, 1);
Screen('TextSize', wPtr, 30);
Screen('DrawText', wPtr, sprintf('press SPACE to start'), text_w - offset_w, text_h + 80, black, gray);
rect = [(screen_size.width / 2) (screen_size.height / 2) (screen_size.width / 2 + 20) (screen_size.height / 2 + 20)];
Screen('FillOval', wPtr, [0,0,0], rect);41
Screen(wPtr, 'Flip', [], 1);
GetChar();
Screen('FillOval', wPtr, gray, rect);
Screen(wPtr, 'Flip');
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [wPtr, wRect, old_pref] = init_screen()
AssertOpenGL;
old_pref = Screen('Preference', 'verbosity', 0); % contorl debuging checks
screenid = max(Screen('Screens'));
HideCursor();
[wPtr, wRect] = Screen('OpenWindow', screenid, 0, [], 32, 2);
white = WhiteIndex(wPtr); % pixel value for white
black = BlackIndex(wPtr); % pixel value for black
Screen('BlendFunction', wPtr, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
gray = (white + black) / 2;
Screen(wPtr, 'FillRect', gray);
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function quit(old_pref)
Screen('CloseAll');
Screen('Preference', 'verbosity', old_pref);
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function show_decks(wPtr, decks, shuffle_decks, rest)
screen_size = Screen('Resolution', 0);
w_space = screen_size.width / 5; % width space
h_space = screen_size.height / 3;
pos_x = w_space / 5; % || s |c| s |c| s |c| s |c| s || there are 5 space in horizon
pos_y = h_space / 6;
card_width = w_space;
card_height = h_space;42
imgA = imread('./images/a.jpeg', 'JPG');
imgB = imread('./images/b.jpeg', 'JPG');
imgC = imread('./images/c.jpeg', 'JPG');
imgD = imread('./images/d.jpeg', 'JPG');
textureA = Screen('MakeTexture', wPtr, double(imgA));
textureB = Screen('MakeTexture', wPtr, double(imgB));
textureC = Screen('MakeTexture', wPtr, double(imgC));
textureD = Screen('MakeTexture', wPtr, double(imgD));
if (decks.index(1,shuffle_decks(1)) > 40)
imgA = imread('./images/blank.jpeg', 'JPG');
end
if (decks.index(1,shuffle_decks(2)) > 40)
imgB = imread('./images/blank.jpeg', 'JPG');
end
if (decks.index(1,shuffle_decks(3)) > 40)
imgC = imread('./images/blank.jpeg', 'JPG');
end
if (decks.index(1,shuffle_decks(4)) > 40)
imgD = imread('./images/blank.jpeg', 'JPG');
end
textureA = Screen('MakeTexture', wPtr, double(imgA));
textureB = Screen('MakeTexture', wPtr, double(imgB));
textureC = Screen('MakeTexture', wPtr, double(imgC));
textureD = Screen('MakeTexture', wPtr, double(imgD));
shadow_offset = [5 5 5 5];
deck_A = [pos_x, pos_y, pos_x + card_width, pos_y + card_height];
deck_A_shadow_1 = deck_A + shadow_offset;
deck_A_shadow_2 = deck_A + 2 * shadow_offset;
deck_A_shadow_3 = deck_A + 3 * shadow_offset;
deck_B = deck_A + [pos_x + card_width, 0, pos_x + card_width, 0];
deck_B_shadow_1 = deck_B + shadow_offset;
deck_B_shadow_2 = deck_B + 2 * shadow_offset;
deck_B_shadow_3 = deck_B + 3 * shadow_offset;
deck_C = deck_B + [pos_x + card_width, 0, pos_x + card_width, 0];
deck_C_shadow_1 = deck_C + shadow_offset;
deck_C_shadow_2 = deck_C + 2 * shadow_offset;
deck_C_shadow_3 = deck_C + 3 * shadow_offset;
deck_D = deck_C + [pos_x + card_width, 0, pos_x + card_width, 0];43
deck_D_shadow_1 = deck_D + shadow_offset;
deck_D_shadow_2 = deck_D + 2 * shadow_offset;
deck_D_shadow_3 = deck_D + 3 * shadow_offset;
Screen('DrawTextures', wPtr, textureA, [], [deck_A', deck_A_shadow_1', deck_A_shadow_2', deck_A_shadow_3']);
Screen('DrawTextures', wPtr, textureB, [], [deck_B', deck_B_shadow_1', deck_B_shadow_2', deck_B_shadow_3']);
Screen('DrawTextures', wPtr, textureC, [], [deck_C', deck_C_shadow_1', deck_C_shadow_2', deck_C_shadow_3']);
Screen('DrawTextures', wPtr, textureD, [], [deck_D', deck_D_shadow_1', deck_D_shadow_2', deck_D_shadow_3']);
screen_size = Screen('Resolution', 0);
white = WhiteIndex(wPtr); % pixel value for white
black = BlackIndex(wPtr); % pixel value for black
gray = (white + black) / 2;
w_space = screen_size.width / 3;
h_space = screen_size.height / 3;
offset = 120;
offset_w = 180;
text_h = h_space * 1.5;
text_w = w_space;
if (rest == 1)
txt_color = gray;
else
txt_color = black;
end
Screen('TextFont', wPtr, char('Helvetica'));
Screen('TextStyle', wPtr, 1);
Screen('TextSize', wPtr, 60);
Screen('DrawText', wPtr, sprintf('Select a Deck'), text_w - offset_w, text_h + offset, txt_color, gray);
Screen(wPtr, 'Flip', [], 1);
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function mark_selected_deck(wPtr, selected_deck, shuffle_decks)
screen_size = Screen('Resolution', 0);
w_space = screen_size.width / 5; % width space
h_space = screen_size.height / 3;
pos_x = w_space / 5; % || s |c| s |c| s |c| s |c| s || there are 5 space in horizon
pos_y = h_space / 6;44
card_width = w_space;
card_height = h_space;
shadow_offset = [5 5 5 5];
deck_A = [pos_x, pos_y, pos_x + card_width, pos_y + card_height];
deck_A_shadow_3 = deck_A + 3 * shadow_offset;
deck_B = deck_A + [pos_x + card_width, 0, pos_x + card_width, 0];
deck_B_shadow_3 = deck_B + 3 * shadow_offset;
deck_C = deck_B + [pos_x + card_width, 0, pos_x + card_width, 0];
deck_C_shadow_3 = deck_C + 3 * shadow_offset;
deck_D = deck_C + [pos_x + card_width, 0, pos_x + card_width, 0];
deck_D_shadow_3 = deck_D + 3 * shadow_offset;
if (selected_deck == 'a' || selected_deck == 'A' || selected_deck == 1)
img = imread('./images/a_sel.jpeg', 'JPG');
deck_shadow = deck_A_shadow_3;
elseif (selected_deck == 'b' || selected_deck == 'B' || selected_deck == 2)
img = imread('./images/b_sel.jpeg', 'JPG');
deck_shadow = deck_B_shadow_3;
elseif (selected_deck == 'c' || selected_deck == 'C' || selected_deck == 3)
img = imread('./images/c_sel.jpeg', 'JPG');
deck_shadow = deck_C_shadow_3;
elseif (selected_deck == 'd' || selected_deck == 'D' || selected_deck == 4)
img = imread('./images/d_sel.jpeg', 'JPG');
deck_shadow = deck_D_shadow_3;
end
texture = Screen('MakeTexture', wPtr, double(img));
Screen('DrawTextures', wPtr, texture, [], [deck_shadow']);
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function show_msg(wPtr, reward, punish, deck)
screen_size = Screen('Resolution', 0);45
w_space = screen_size.width / 3;
h_space = screen_size.height / 3;
offset = 120;
offset_w = 180;
text_h = h_space * 1.5;
text_w = w_space;
msg_text1 = sprintf('You won: ');
msg_text2 = sprintf('But lost: ');
white = WhiteIndex(wPtr); % pixel value for white
black = BlackIndex(wPtr); % pixel value for black
gray = (white + black) / 2;
mark_selected_deck(wPtr, deck)
Screen('TextFont', wPtr, char('Helvetica'));
Screen('TextStyle', wPtr, 1);
Screen('TextSize', wPtr, 60);
% clear old text
Screen('DrawText', wPtr, sprintf('Select a Deck'), text_w - offset_w, text_h + offset, gray, gray);
% show reward and punishment
Screen('DrawText', wPtr, msg_text1, text_w - offset_w, text_h, black, gray);
Screen('DrawText', wPtr, sprintf(' %d', reward), text_w + offset_w, text_h, black, gray);
if (punish == 0)
% nothing
else
Screen('DrawText', wPtr, msg_text2, text_w - offset_w, text_h + offset, black, gray);
Screen('DrawText', wPtr, sprintf(' %d', punish), text_w + offset_w, text_h + offset, black, gray); % other
numbers are left aligned
end
Screen('Flip', wPtr);
tic
while toc < 3 end;
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function wait_for_triger(triger_handle)
IOPort('Purge', triger_handle);
triger_data = 0;
while (triger_data ~= 48)46
if (IOPort('BytesAvailable', triger_handle))
[triger_data, when, errmsg] = IOPort('Read', triger_handle, 1, 1);
end
end
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [key, when] = read_response_box(wPtr, resp_handle, resp_timer)
IOPort('Purge', resp_handle);
rand_key = randperm(4);
read_key = 0;
key = rand_key(1);
while((toc(resp_timer) < 4) && (read_key == 0))
if (IOPort('BytesAvailable', resp_handle))
[key, when, errmsg] = IOPort('Read', resp_handle, 1, 1);
n = IOPort('BytesAvailable', resp_handle);
[date_dummy, when, errmsg] = IOPort('Read', resp_handle, 1, n);
fprintf('Resp: %d\n', key);
read_key = 1;
end
end
if (read_key == 0)
fprintf('Random res: %d\n', key);
when = 0;
end
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function decks=penalty_dist(NumberofCards)
decks.reward = zeros(4,NumberofCards);
decks.punish = zeros(4,NumberofCards);
decks.index = ones(1,4); % current index of top card on decks47
decks.names = ['A', 'B', 'C', 'D'];
for i=1 : NumberofCards
decks.reward(1,i) = 100;
decks.reward(2,i) = 100;
decks.reward(3,i) = 50;
decks.reward(4,i) = 50;
end
penalty=zeros(4,40);
penalty(1,3) = 150;
penalty(1,5) = 300;
penalty(1,7) = 200;
penalty(1,9) = 250;
penalty(1,10)= 350;
penalty(1,12)= 350;
penalty(1,14)= 250;
penalty(1,15)= 200;
penalty(1,17)= 300;
penalty(1,18)= 150;
penalty(1,22)= 300;
penalty(1,24)= 350;
penalty(1,26)= 200;
penalty(1,27)= 250;
penalty(1,28)= 150;
penalty(1,31)= 350;
penalty(1,32)= 200;
penalty(1,33)= 250;
penalty(1,37)= 150;
penalty(1,38)= 300;
penalty(2,9) = 1250;
penalty(2,14)= 1250;
penalty(2,21)= 1250;
penalty(2,32)= 1250;
penalty(3,3) = 50;
penalty(3,5) = 50;
penalty(3,7) = 50;
penalty(3,9) = 50;
penalty(3,10)= 50;
penalty(3,12)= 25;
penalty(3,13)= 75;
penalty(3,17)= 25;
penalty(3,18)= 75;
penalty(3,20)= 50;
penalty(3,24)= 50;
penalty(3,25)= 25;
penalty(3,26)= 50;
penalty(3,29)= 75;
penalty(3,30)= 50;
penalty(3,34)= 25;
penalty(3,35)= 25;48
penalty(3,37)= 75;
penalty(3,39)= 50;
penalty(3,40)= 75;
penalty(4,10)= 250;
penalty(4,20)= 250;
penalty(4,29)= 250;
penalty(4,35)= 250;
decks.punish = penalty;
end