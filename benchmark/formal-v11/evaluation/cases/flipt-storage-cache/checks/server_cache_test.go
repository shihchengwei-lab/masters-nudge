package cmd

import (
    "context"
    "net"
    "os"
    "path/filepath"
    "testing"
    "time"
    "github.com/stretchr/testify/require"
    shared "go.flipt.io/flipt/internal/cache"
    "go.flipt.io/flipt/internal/config"
    "go.flipt.io/flipt/internal/info"
    "go.flipt.io/flipt/rpc/flipt"
    "go.uber.org/zap"
    "google.golang.org/grpc"
    "google.golang.org/grpc/metadata"
    "google.golang.org/grpc/test/bufconn"
    "github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
)

type contractCacheHandler interface {
    Evaluate(context.Context,*flipt.EvaluationRequest)(*flipt.EvaluationResponse,error)
}
type contractCacheCounter struct { calls int; marked bool }
func (s *contractCacheCounter) Evaluate(ctx context.Context,r *flipt.EvaluationRequest)(*flipt.EvaluationResponse,error) {
    s.calls++
    s.marked=shared.IsDoNotStore(ctx)
    return &flipt.EvaluationResponse{FlagKey:r.FlagKey,EntityId:r.EntityId},nil
}

// Exercise the server's actual interceptor chain. No assertions about variable
// names, assignment count, or the internal layout of NewGRPCServer are used.
func TestContractServerEvaluationCacheIsConnected(t *testing.T) {
    cfg:=config.DefaultConfig()
    cfg.Meta.CheckForUpdates=false;cfg.Meta.TelemetryEnabled=false
    cfg.Server.Host="127.0.0.1";cfg.Server.GRPCPort=0
    cfg.Storage.Type=config.LocalStorageType
    cfg.Storage.Local=&config.Local{Path:t.TempDir()}
    require.NoError(t,os.WriteFile(filepath.Join(cfg.Storage.Local.Path,"features.yml"),[]byte("namespace: default\nflags: []\nsegments: []\n"),0600))
    cfg.Cache.Enabled=true;cfg.Cache.Backend=config.CacheMemory;cfg.Cache.TTL=time.Minute
    ctx,cancel:=context.WithTimeout(context.Background(),15*time.Second);defer cancel()
    server,err:=NewGRPCServer(ctx,zap.NewNop(),cfg,info.Flipt{},false)
    require.NoError(t,err)
    defer server.Shutdown(context.Background())
    counter:=&contractCacheCounter{}
    server.RegisterService(&grpc.ServiceDesc{
        ServiceName:"fixed.ContractCache",HandlerType:(*contractCacheHandler)(nil),
        Methods:[]grpc.MethodDesc{{MethodName:"Evaluate",Handler:func(srv interface{},ctx context.Context,decode func(interface{})error,intercept grpc.UnaryServerInterceptor)(interface{},error){
            req:=&flipt.EvaluationRequest{}
            if err:=decode(req);err!=nil{return nil,err}
            handler:=func(ctx context.Context,r interface{})(interface{},error){return srv.(contractCacheHandler).Evaluate(ctx,r.(*flipt.EvaluationRequest))}
            if intercept==nil{return handler(ctx,req)}
            return intercept(ctx,req,&grpc.UnaryServerInfo{Server:srv,FullMethod:"/fixed.ContractCache/Evaluate"},handler)
        }}},
    },counter)
    listener:=bufconn.Listen(1024*1024);defer listener.Close()
    go server.Serve(listener)
    conn,err:=grpc.DialContext(ctx,"fixed",grpc.WithInsecure(),grpc.WithBlock(),grpc.WithContextDialer(func(context.Context,string)(net.Conn,error){return listener.Dial()}))
    require.NoError(t,err);defer conn.Close()
    req:=&flipt.EvaluationRequest{FlagKey:"example",EntityId:"same",NamespaceKey:"default"}
    for i:=0;i<2;i++{require.NoError(t,conn.Invoke(ctx,"/fixed.ContractCache/Evaluate",req,&flipt.EvaluationResponse{}))}
    require.Equal(t,1,counter.calls,"enabling the server cache must reuse an evaluation response")
    req.EntityId="not-cached"
    marked:=metadata.NewOutgoingContext(ctx,metadata.Pairs(runtime.MetadataPrefix+"cache-control","no-store"))
    require.NoError(t,conn.Invoke(marked,"/fixed.ContractCache/Evaluate",req,&flipt.EvaluationResponse{}))
    require.True(t,counter.marked,"the server must forward the no-store mark to the request handler")
}
