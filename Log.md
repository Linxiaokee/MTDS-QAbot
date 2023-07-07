# Log

* version0 问题匹配，返回答案

* version1 答案作为数据，问题作为metadata，self-querying retrieval
  * 7.1 note：
    * 基本功能完成（branch v1）
    * 问题作为 metadata 没有意义，metadata 需要是准确的信息
  
* version2 形成chatbot
  * 7.3 note：
    * 基本功能完成，效果尚可
  
* version3 划定问题边界，llm引导用户
  * 7.3 note：
    
    * 尝试拆分 retrieval_qa_chain
    
      ​	7.3 evening update: 
    
      ​		failed, due to: 不会写 chain
    
      ​		instead: prompt engineering