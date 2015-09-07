namespace java com.dinglicom.cloud.jmp.thrift  


struct AppMessage {
  1: string appId;  
  2: string appName;  
  3: string appType;  
  4: string path;
  5: string userName
}

//;;描述：
//;;	appId ：app的唯一标识
//;;	appType ："0" jar ,"1" web ,"mr" 2
 
service AppRpcService {
  string startApp(1:AppMessage appMessage);  
  string stopApp(1:AppMessage appMessage)
}

