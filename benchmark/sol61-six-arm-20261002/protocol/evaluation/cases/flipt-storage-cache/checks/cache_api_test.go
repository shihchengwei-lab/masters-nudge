package cache

import (
    "context"
    "errors"
    "testing"
    "github.com/stretchr/testify/require"
    shared "go.flipt.io/flipt/internal/cache"
    "go.flipt.io/flipt/rpc/flipt"
    "go.uber.org/zap/zaptest"
)

func TestContractProtoBoundaries(t *testing.T) {
    for _, tc := range []struct{name string; cached bool; value []byte; err error}{
        {"miss",false,nil,nil}, {"corrupt",true,[]byte{255},nil},
        {"cache_error",false,nil,errors.New("read failed")},
    } {
        t.Run(tc.name,func(t *testing.T){
            spy:=&cacheSpy{cached:tc.cached,cachedValue:tc.value,getErr:tc.err}
            s:=NewStore(&storeMock{},spy,zaptest.NewLogger(t))
            require.False(t,s.getProto(context.Background(),"key",&flipt.Flag{}))
        })
    }
    spy:=&cacheSpy{}
    s:=NewStore(&storeMock{},spy,zaptest.NewLogger(t))
    // Invalid UTF-8 cannot be encoded in a protobuf string.
    s.setProto(context.Background(),"key",&flipt.Flag{Key:string([]byte{255})})
    require.Empty(t,spy.cacheKey)
    expected:=errors.New("store failed")
    source:=&storeMock{}
    source.On("GetFlag",context.Background(),"ns","key").Return((*flipt.Flag)(nil),expected)
    s=NewStore(source,&cacheSpy{},zaptest.NewLogger(t))
    _,err:=s.GetFlag(context.Background(),"ns","key")
    require.Same(t,expected,err)
    success:=&storeMock{}
    flag:=&flipt.Flag{Key:"key",NamespaceKey:"ns"}
    success.On("GetFlag",context.Background(),"ns","key").Return(flag,nil)
    written:=&cacheSpy{}
    s=NewStore(success,written,zaptest.NewLogger(t))
    got,err:=s.GetFlag(context.Background(),"ns","key")
    require.NoError(t,err)
    require.Equal(t,flag,got)
    require.Equal(t,"s:f:ns:key",written.cacheKey)
    require.NotEmpty(t,written.cachedValue)
    require.False(t,shared.IsDoNotStore(context.Background()))
    require.True(t,shared.IsDoNotStore(shared.WithDoNotStore(context.Background())))
    require.False(t,shared.IsDoNotStore(context.WithValue(context.Background(),"do-not-store",true)))
}
