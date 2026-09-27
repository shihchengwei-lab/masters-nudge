package grpc_middleware

import (
    "context"
    "errors"
    "testing"
    "time"
    "github.com/stretchr/testify/require"
    "go.flipt.io/flipt/internal/cache/memory"
    "go.flipt.io/flipt/internal/config"
    "go.flipt.io/flipt/rpc/flipt"
    "go.uber.org/zap/zaptest"
    g "google.golang.org/grpc"
)

func TestContractInterceptorBoundaries(t *testing.T) {
    response:=&flipt.Flag{Key:"unchanged"}
    expected:=errors.New("handler failure")
    actual,err:=CacheControlUnaryInterceptor(context.Background(),nil,&g.UnaryServerInfo{},func(context.Context,interface{})(interface{},error){return response,expected})
    require.Same(t,response,actual)
    require.Same(t,expected,err)
    cache:=memory.NewCache(config.CacheConfig{TTL:time.Second,Enabled:true,Backend:config.CacheMemory})
    interceptor:=EvaluationCacheUnaryInterceptor(cache,zaptest.NewLogger(t))
    calls:=0
    handler:=func(context.Context,interface{})(interface{},error){calls++;return &flipt.Flag{Key:"flag"},nil}
    for i:=0;i<2;i++{_,err=interceptor(context.Background(),&flipt.GetFlagRequest{Key:"flag"},&g.UnaryServerInfo{},handler);require.NoError(t,err)}
    require.Equal(t,2,calls,"GetFlag must not be served by the evaluation response cache")
}
