# from paddle.nn import Layer, Linear

# class AsteriskRegressor(Layer):
#     '''
#     该类需要继承paddle.nn.Layer父类，并且在类中定义init函数和forward函数。
#     forward函数是框架指定实现前向计算逻辑的函数，程序在调用模型实例时会自动执行，forward函数中使用的网络层需要在init函数中声明。
#     '''

    

#     # self代表类的实例自身
#     def __init__(self,input_features:int = 0,output_features:int = 0):
#         # 初始化父类中的一些参数
#         super(AsteriskRegressor, self).__init__()
        
#         # 定义一层全连接层，输入维度是13，输出维度是1
#         self.fc = Linear(in_features=input_features, out_features=output_features)
    
#     # 网络的前向计算
#     def forward(self, inputs):
#         x = self.fc(inputs)
#         return x