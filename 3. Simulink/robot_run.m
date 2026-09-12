close % 关闭当前的Figure窗口
clear % 清除工作空间的所有变量
clc   % 清除命令窗口的内容，对工作环境中的全部变量无任何影响

%添加模型路径
allpaths = genpath('.'); % 获取当前目录及其子目录的所有路径
addpath(allpaths);

