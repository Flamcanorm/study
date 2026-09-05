>[golang 공식 페이지](https://go.dev/doc/tutorial/getting-started)
>
>Go programmers writing data-race-free programs can rely on sequentially consistent execution of those programs, just as in essentially all other modern programming languages.  
  When it comes to programs with races, both programmers and compilers should remember the advice: "don't be clever."

>Don't communicate by sharing memory, share memory by communicating.

# 특징


## CSP(Communicating Sequential Processes) 방식의 Concurrent 지원

- IPC 과정에서 서로 데이터를 주고 받는게 아닌 Channel 이라는 매개체를 통해서 메세지를 전달하며 통신하는 모델.
- 메모리를 통해서 통신하지 않고 통신을 해서 메모리를 공유 (공유 메모리 방식은 Lock 등의 동기화 문제가 복잡하므로 메세지 패싱 방식을 사용한다는 뜻)
- 기존의 메세지 패싱 방식의 사용자 모드와 커널 모드간의 전환 오버헤드가 Go 언어에선 Go 런타임이 사용자 영역에서 채널을 생성하기 때문에 오버헤드 없이 메모리 복사만으로 빠르게 통신이 가능.


## Goroutine 을 통한 매우 가벼운 비동기 Concurrent 처리 구현 
>[goroutine](golang.md#goroutine)

- 사용자 공간 기반의 경량 스케줄링
	- [Go 런타임](golang.md#Go%20런타임) 은 커널 영역이 아닌 사용자 공간에 존재하며, 하나의 실행 파일에 빌드되어 포함된다.
	- 이로 인해 goroutine 간의 Context Switching이나 채널을 통한 메세지 전달 시, 모드 전환의 오버헤드가 발생하지 않아 goroutine이 매우 많아도 빠르게 실행될 수 있다.



## 동적 스택 확장 (Dynamic Stack Growth)

- [goroutine](golang.md#goroutine)이 생성될 때 2KB 크기의 아주 작은 스택을 가짐
- 실행 중 스택 메모리가 더 필요해지면 Go 런타임에서 이를 감지하여 기존 스택의 크기를 2배 늘려 새로운 메모리 공간을 유저 영역에 할당하고 기존 데이터를 모두 복사하고 포인털르 이동시킴
- 스택오버플로우 방지


## 네트워크 폴러 (Netpoller)를 통한 I/O 비동기 최적화

- goroutine이 네트워크 리소스를 기다려야 하는 상황 (Socket Read/Write)이면, 원래는 OS 스레드가 block 됨
- Go 런타임은 내부에 OS별 비동기 I/O 시스템(Linux `epoll`, macOS `kqueue`, Windows `IOCP`)을 추상화한 [netpoller](golang.md#netpoller)를 둠
- goroutine이 네트워크 대기가 발생한다면 해당 goroutine을 netpoller에게 전달하고 스레드는 다른 goroutine을 실행함
- 개발자는 동기식으로 코드를 짜지만 내부적으로는 비동기 I/O가 작동하여 효율을 높임


## 동시 가비지 컬렉터 (Concurrent GC)

- 가비지 컬렉터에 의해 모든 스레드가 멈추는 STW 현상을 막아줌 (아주 짧아짐)
- 백그라운드에서 가비지 컬렉터를 실행하여 스레드가 멈추지 않고 계속 실행됨





# goroutine
```go
func say() {
	// ...
}

go say() // goroutine 키워드 go 를 사용해 say() 함수 실행
```
> Go 언어에서의 멀티 스레드 구현

- Go 런타임에서 관리하는 Lightweight 논리적 스레드 (사용자 영역)
- 기존의 스레드보다 훨씬 적은 메모리 크기로 동작. (kb)
- 하나의 스레드 내부에서 [Multiplexing 구조](golang.md#Multiplexing%20구조)을 사용하여 여러 가상 스레드를 처리
	- 기존 스레드보다 많은 양의 스레드를 생성할 수 있어서 효율적임.
- 기본적으로 1개의 CPU에서 처리하기 떄문에 동시성 (Concurrency) 임.
	-  만약 여러 개의 CPU를 사용하려면 (Parallel), `runtime.GOMAXPROCS(cpu개수)`([GOMAXPROCS](golang.md#GOMAXPROCS))함수를 호출하여야한다. (`cpu개수`는 Logical CPU 수를 의미)





# gochannel
```go
package main
 
func main() {
  // 정수형 채널을 생성한다 
  ch := make(chan int) // make() 함수로 채널 생성
 
  go func() { // 익명함수로 Goroutine 실행
    ch <- 123   //채널에 123을 보낸다
  }()
 
  var i int
  i = <- ch  // 채널로부터 123을 받는다
  println(i)
}
```
> goroutine도 멀티 스레드이기 때문에 Data Race 발생, [mutexLock](mutexLock.md) 을 지원하지만 gochannel 방식이 있음.

- 스레드 간의 통신할 때 별도의 Lock을 걸지 않아도 Go에서 자동으로 데이터를 동기화 시켜줌.
	- 채널에서 데이터를 넣거나(`ch <- data`) 뺄 때(`<-ch`), 데이터가 준비될 때까지 goroutine이 알아서 대기(Block)함.
	- 예를 들어 goroutine으로 스레드를 10개 만들어 이미지 10,000개를 처리한다면 메인 프로그램에서 이 작업이 모두 끝났는지 알 수 없어 먼저 종료되어 버릴 수 있으나 gochannel을 사용하여 10개의 스레드가 각자 작업이 끝날 때마다 `done` 메세지를 채널에 보낸다면, 메인 프로그램에서 채널에 `done` 메세지고 10개 모두 도착할 때까지 기다렸다가 프로그램을 종료할 수 있음.





# Go 런타임

## Go 스케줄러 
> 출처 : [1](https://medium.com/@sharmasarvesh826/understanding-the-go-scheduler-the-gmp-model-explained-dee532c15c5f), [2](https://www.linkedin.com/pulse/inside-go-scheduler-understanding-g-m-p-model-sandeep-shewalkar-zquef), [3](https://velog.io/@sunaookamisiroko/Goroutine-%EC%8A%A4%EC%BC%80%EC%A4%84%EB%A7%81), [youtube Gopher Academy](https://www.youtube.com/watch?v=wQpC99Xu1U4)


### 스케줄러 작동 방식
>[GMP Model](golang.md#GMP%20Model)

![](../05_attachments/Pasted%20image%2020260709035249.png)
> Go Scheduler

![](../05_attachments/Pasted%20image%2020260709035319.png)
>1. `M`은 `P0`의 [Local Run Queue](golang.md#Local%20Run%20Queue)에서 `G`를 가져와 실행한다.
>2. `G`의 실행이 종료되면, `M`은 `P0`의 [Local Run Queue](golang.md#Local%20Run%20Queue)에 실행할 `G`가 있는지 확인한다.
>3. 만약 존재한다면, 가져와서 실행한다.
> 참고 : [P 구조체](golang.md#P%20구조체)

![](../05_attachments/Pasted%20image%2020260709035650.png)
>4. 이제 모든 `G`를 실행하여 [Local Run Queue](golang.md#Local%20Run%20Queue)가 비었다.
>5. 그렇다면, [Global Run Queue](golang.md#Global%20Run%20Queue)에 실행할 `G`가 있는지 확인한다.
>6. 만약 존재한다면, `global runqueue의 현재 길이/GOMAXPROCS + 1` 만큼 `G`를 가져온다
>참고 : [워크 스틸링 (Work Stealing)](#워크%20스틸링%20(Work%20Stealing))

![](../05_attachments/Pasted%20image%2020260709040040.png)
>7. 이제 [Global Run Queue](golang.md#Global%20Run%20Queue)가 비었다.
>8. 그렇다면, [netpoller](golang.md#netpoller)에 준비된 `G`가 있는지 확인한다.
>9. 만약 존재한다면, 가져와서 실행한다.

![](../05_attachments/Pasted%20image%2020260709040703.png)
>10. 이제 [netpoller](golang.md#netpoller)도 비었다.
>11. 그렇다면, 이제부터는 랜덤하게 `P`를 하나를 선택한다.
>12. 그리고 선택한 `P`의 [Local Run Queue](golang.md#Local%20Run%20Queue)의 **반을 가져온다.**
>13. 가져온 `G`를 실행한다.
>참고 : [워크 스틸링 (Work Stealing)](#워크%20스틸링%20(Work%20Stealing))

![](../05_attachments/Pasted%20image%2020260709040857.png)





### 공정성
>`G`의 실행시간이 매우 길어 다른 `G`들이 기아(Starve) 상태에 빠지거나 Convoy Effect가 발생한다면 어떻게 해결할 것인가

![](../05_attachments/Pasted%20image%2020260709042314.png)
이를 해결하기 위해 간단한 방법으로 SJF 스케줄링을 할 수 있다. 하지만 SJF 스케줄링은 `G`의 실행 시간을 미리 알아야하는 한계가 존재하기 때문에 사실 거의 불가능하다고 말할 수 있다.

다른 방법으로 Preemptive Scheduling (선점형 스케줄링) 과 Cooperative Scheduling(비선점형 스케줄링) 방식이 있다.

- 선점형 스케줄링은 일정 시간이 지나면 태스크로부터 자원(CPU)을 빼앗아 다른 태스크에게 넘겨주는 스케줄링 방식이다.
- 비선점형 스케줄링은 태스크가 완료될 때까지 자원을 독점하는 스케줄링 방식이다.

Go의 경우 비선점형 스케줄링을 사용하였으나, 1.14 버전부터 선점형 스케줄링을 사용한다.

![](../05_attachments/Pasted%20image%2020260709042417.png)

각 `G`는 10ms 시간을 할당받는다. 10ms가 지난다면, SIGURG signal이 발생해 선점당한다. 우리가 흔히 아는 커널 영역에서의 인터럽트와 비슷하지만, signal이 userspace에서 일어난다는 점에서 다르다. (Go 런타임은 userspace에 존재하고 이곳에서 goroutine을 관리한다.)

signal은 선점 당할 `G`가 실행되고 있는 `M`에 전달된다.

그렇다면 이 signal는 누가 보내줄까? 바로 **sysmon**이라는 쓰레드가 한다.

#### sysmon

![](../05_attachments/Pasted%20image%2020260709042835.png)
Go 런타임에 존재하는 Daemon thread로 `P`없이 `G`를 실행하며, goroutine들을 모니터링 하는 역할을 한다.

![](../05_attachments/Pasted%20image%2020260709042959.png)

어떤 `G`의 실행 시간이 10ms가 넘으면, 해당 `G`를 실행하고 있는 `M`에게 선점 signal을 보낸다. **선점 signal을 받은 `M`은 `G`를 [Global Run Queue](golang.md#Global%20Run%20Queue)에 보내게 된다.**




#### goroutine locality

`G`는 또 다른 `G`를 생성할 수 있다.

![](../05_attachments/Pasted%20image%2020260709043308.png)

큐를 사용하면 FIFO 방식으로 각 `G`가 동등하게 실행될 수 있으므로 공정하다. 하지만 locality 면에서 좋지 않다.

방금 생성한 `G`를 다른 `G`를 전부 처리하고 나서 참조하기 때문에 프로세서의 캐시, 스택을 사용하지 못하기 때문이다.




#### Time slice inheritance

![](../05_attachments/Pasted%20image%2020260709044240.png)
locality 문제를 해결하가 위해 Go 스케줄러는 `G`가 만들어지면, [Local Run Queue](golang.md#Local%20Run%20Queue)의 tail 대신에 head에 넣는다. (`runnext` 라는 별도의 독립된 포인터에 들어간다. `M`이 `G`를 꺼낼 때 `runnext` -> `local queue` 순서로 가져감)

이렇게 하면 locality를 해결할 수 있다. 하지만 **만약 `G`가 끊임없이 생성되는 경우, local runqueue의 나머지 `G`들은 기아 상태에 빠지게 된다. 게다가 local runqueue가 비질 않으니 global runqueue의 `G`들 또한 기아 상태에 빠지게 된다.**

이를 해결하기 위해 Go scheduler는 **Time Slice Inheritance**를 사용한다.

![](../05_attachments/Pasted%20image%2020260709044251.png)
> 생성한 자식 goroutine에게 자신의 남은 잔여 시간을 상속한다

`ParentGoroutine`은 10ms의 실행 시간을 가지고, 3ms 시점에 `ChildGoroutine1`을 생성했다고 생각해보자.

그렇다면 `ChildGoroutine1`은 **10ms - 3ms = 7ms**의 실행 시간을 갖게 된다. 이어서 `ChildGoroutine1`이 4ms 시점에 새로운 `ChildGoroutine2`를 생성했다고 생각해보자.

그렇다면 `ChildGoroutine2`은 **7ms - 4ms = 3ms**의 실행 시간을 갖게 된다.

이렇게 부모와 자식 `G`들을 합쳐서 무조건 **총 10ms의 실행 시간**을 부여해 다른 `G`의 기아 상태를 방지한다.

여기까지 이 방법으로 local runqueue의 기아 상태는 해결하겠지만, [Global Run Queue](golang.md#Global%20Run%20Queue)의 기아 상태는 해결하지 못한다. `M`이 [Global Run Queue](golang.md#Global%20Run%20Queue)의 `G`를 가져올 때는 [Local Run Queue](golang.md#Local%20Run%20Queue)가 비었을 때다. **즉, local runqueue에 항상 `G`가 존재한다면, global runqueue의 `G`를 절대 가져오지 않는다.**

이를 해결하기 위해 Go scheduler는 **어떤 조건을 만족하면 global runqueue에서 `G`를 가져오게 된다.**




#### schedtick
>[Global Run Queue](golang.md#Global%20Run%20Queue)의 기아 상태를 방지하기 위해 Go 런타임은 일정 주기마다 반드시 Global Run Queue를 polling해 `G`를 가져온다.

go runtime에는 `schedtick`이라는 변수가 존재하며, 이 변수는 [Local Run Queue](golang.md#Local%20Run%20Queue)의 **polling**이 한 번 일어날 때마다 증가한다.

polling은 어떤 장치나 프로그램의 상태를 주기적으로 살핀다는 의미이며, 여기서는 `G` 하나를 수행하고 나서 다음으로 실행할 `G`를 찾기 위해 runqueue를 살피는 것을 뜻한다.

[Global Run Queue](golang.md#Global%20Run%20Queue)를 반드시 polling하게 되는 조건은 다음과 같다.

```go
if schedtick % 61 == 0 {
	getFromGlobalRunqueue()
} else {
	doThingsAsBefore()
}
```

즉, `schedtick` 변수가 61이 되면 global runqueue를 반드시 polling해서 `G`를 가져온다.

61이라는 숫자는 성능적으로 테스트한 범위에서 제일 결과가 좋았던 소수를 가져온 것이다. 이보다 너무 크면 기아 상태를 해결하지 못하고, 너무 작으면 global runqueue에 polling을 자주 하게 되어 lock때문에 성능 저하를 일으킨다.

##### 왜 소수일까?
>`schedtick` 변수가 61이 되면 polling 하는 이유

go scheduler는 실행할 새로운 application을 불러들이거나, 실행할 새 goroutine을 찾는 주기를 갖고 있는데, 이는 2나 16, 32같은 2의 거듭제곱으로 나타낼 수 있다. 물론 다른 숫자가 불가능하지는 않지만 가능성이 낮다.

만약 이 주기들이 겹치게 되면 go scheduler는 동시에 실행되면 안되므로 lock을 걸어야 한다. 따라서 scheduler에 lock이 걸린 동안 scheduler가 필요한 다른 작업들은 멈추게 되어 성능 저하가 일어난다.

즉, 새 application을 불러들이는 작업과 global runqueue를 polling하는 작업이 겹친다면, 둘 중 하나가 기다려야 하므로 성능 저하가 발생한다는 것이다.

![](../05_attachments/Pasted%20image%2020260709045307.png)

위 그래프에서 주황색 선은 scheduler가 새 application을 불러들이는 주기고 8이다.

파란색 선은 61의 주기이고 빨간색 선은 64의 주기다.

빨간색 선이 0이 될 때마다 주황색 선도 같이 0이 된다. 충돌이 일어난다는 뜻이다.

그러나 파란색 선은 그것을 비껴간다. 따라서 소수를 사용한다.

(이는 해시 맵에서 버킷의 크기를 소수로 정하는 것과 비슷하다)




#### syscall block

![](../05_attachments/Pasted%20image%2020260709045851.png)

만약 `G`의 system call로 인해 `M`이 block됐다면 어떡할까? 아직 `P`의 local runqueue에는 실행되야 할 `G`들이 많은데 말이다.

Go scheduler는 **`P`를 다른 `M`에게 건내주어([Hand-off Mechanism](golang.md#Hand-off%20Mechanism)) 이를 해결한다.**

![](../05_attachments/Pasted%20image%2020260709050227.png)

![](../05_attachments/Pasted%20image%2020260709050230.png)

`G`의 system call로 인해 `M`이 block당하면, **`P`와 `M`-`G`를 통째로 분리시킨다.** 이후에 다른 `M`을 생성하거나, idle 상태였던 `M`을 가져와 연결시킨다.

근데 만약 idle 상태인 `M`이 존재했다면 상관 없지만 새로 만들어야 한다면 그 비용은 비싸다. 또, 모든 system call이 긴 시간이 걸리는 것은 아니기 때문에 짧은 system call에도 hand off를 남발한다면 성능상 문제가 생길 것이다.

따라서 scheduler는 긴 시간이 걸린다는 걸 알 수 있는 system call에만 즉시 hand off를 사용한다. 나머지 짧은 system call에는 block당한 상태로 내비둔다. system call로부터 값을 return 받으면 unblock되고 다시 일을 재개한다.

![](../05_attachments/Pasted%20image%2020260709050358.png)

**하지만 짧은 시간이 걸린다고 예측한 system call이 여러 사유에 의해 오래 걸릴 수 있다. 이런 경우에는 지켜보고 있던 [sysmon](golang.md#sysmon)이 handoff를 실행한다.**

system call이 끝나고 나면 block당한 `M`-`G`는 unblock된다.

scheduler는 locality를 유지하기 위해 `G`를 system call 전에 있었던 `P`에 넣으려고 시도한다. 만약 이것이 불가능하다면, idle 상태의 다른 `P`에 넣는다. 

idle 상태의 `P`가 존재하지 않는다면 global queue에 넣는다.





### 스케줄러 관련

#### GMP Model
- **G (Goroutine) :** 고루틴 그 자체를 의미.
	- 논리적인 실행 단위이며, goroutine의 상태(실행, 대기 등), 프로그램 카운터(PC), 그리고 자체적인 스택 포인터를 가지고 있는 구조체.
- **M (Machine / OS Thread) :** OS의 실제 커널 스레드를 의미.
	- 메모리를 할당받고 CPU 위에서 실제로 코드를 실행하는 물리적 주체. G가 실행되기 위해 반드시 M이 필요.
- **P (Processor) :** 논리적 프로세서로 코드를 실행하기 위한 Context
	- 기본적으로 컴퓨터의 CPU 코어 개수만큼 생성.
	- M이 G를 실행하기위해 반드시 P에 할당되어야함.



#### Multiplexing 구조
- *N*개의 gorountine을 *M*개의 OS 스레드에 매핑하는 **M:N 모델** 사용.
- ![](../05_attachments/Pasted%20image%2020260709032909.png)
- ![](../05_attachments/Pasted%20image%2020260709030145.png)
- `M`은 커널 스레드, `G`는 goroutine을 의미함. 일반적으로 `M`의 개수보다 `G`의 개수가 많음.




#### 워크 스틸링 (Work Stealing)
- 특정 스레드(***M***)가 자기 ***P***의 로컬 큐에 있던 ***G***를 모두 완료하여 idle 상태라면 다음의 순서로 ***G***를 가져온다. (Stealing)
	- 1. ***Global Run Queu***에 ***G***가 있는지 확인하고 가져옴. (`global runqueue의 현재 길이/GOMAXPROCS +1` 만큼 가져옴)
	- 2. 글로벌 큐가 비었다면, 다른 ***P***의 로컬 큐를 무작위로 조회하여 그곳에서 큐의 절반을 가져와 작업함.




#### Hand-off Mechanism
- 만약 어떤 goroutine이 파일 읽기, 쓰기와 같은 System Call을 호출하면 블록되고 OS 커널 스레드 자체가 멈춘다. (Block)
- 이를 해결하기 위해 Go 런타임은 다음과 같이 작동함.
	- 1. 커널 스레드 (M1)이 시스템 콜로 멈추기 직전, 자기가 가지고 있던 [P](golang.md#P%20구조체)를 방출(Hand-off)함.
	- 2. 대기하고 있던 다른 스레드(M2)를 깨우거나 새로 만들어 방출한 [P](golang.md#P%20구조체)와 결합.
	- 3. M2는 [P](golang.md#P%20구조체)의 로컬 큐에 남아있던 다른 goroutine들을 멈추지 않고 계속 실행.
	- 4. 나중에 시스템 콜을 마친 M1이 돌아와 빈 [P](golang.md#P%20구조체)가 있는지 찾고, 없다면 자신이 실행하던 G1을 글로벌 큐에 넣은 뒤 자신의 스레드 풀로 돌아가 대기함.




#### GOMAXPROCS
>The GOMAXPROCS variable limits the number of operating system threads that can execute user-level Go code simultaneously. There is no limit to the number of threads that can be blocked in system calls on behalf of Go code; those do not count against the GOMAXPROCS limit.

- GOMAXPROCS 변수는 코드를 동시에 실행하는 OS 스레드의 개수를 제한한다.
	- GOMAXPROCS가 6이라면, 코드를 실행하는 OS 스레드의 개수는 6개가 최대이다.
	- system call로 block된 스레드는 GOMAXPROCS에 해당하지 않는다.
		- 즉, 6개의 실행중인 스레드를 제외하고 block된 다른 많은 스레드를 가질 수 있다.




#### P 구조체
![](../05_attachments/Pasted%20image%2020260709032620.png)
- ***P*** 구조체는 heap에 할당되는 자료 구조
- ***P***는 하나의 ***M***에 할당된다. 따라서 ***P***는 [GOMAXPROCS](golang.md#GOMAXPROCS) 의 개수와 같다.
	- ***M***은 ***G***를 실행하기 위해 ***P***를 참조하게 된다.
	- [워크 스틸링 (Work Stealing)](golang.md#워크%20스틸링%20(Work%20Stealing)) 을 위해 체크해봐야 할 스레드의 개수가 무한하다는 문제를 ***P***구조체를 사용함으로써 ***P***의 개수가 [GOMAXPROCS](golang.md#GOMAXPROCS) 와 같기 때문에 유한하게 되었으므로 해결됨 (***P***들만 체크하면 된다)
- [Local Run Queue](golang.md#Local%20Run%20Queue) 뿐만 아니라 코드를 실행하기 위해 ***M***이 유지하고 있던 context도 모두 ***P***에 저장한다.
- ***P*** 구조체를 사용함으로써 block된 ***M***이 ***P***를 다른 ***M***에게 [Local Run Queue](golang.md#Local%20Run%20Queue)과 함께 넘겨줄 수 있다. 




#### Local Run Queue 
![](../05_attachments/Pasted%20image%2020260709030821.png)
- 모든 ***P*** 는 자신만의 로컬 큐를 가지고 있으며, 여기에 실행 대기 중인 ***G*** 들을 보관 (참고 : [P 구조체](golang.md#P%20구조체))
- 최대 256개의 ***G*** 를 큐에 보관 가능 (go 1.17.2 기준)
- ***M*** 이 다음 작업 (***G***)를 꺼낼 때, 자기 ***P***의 로컬 큐에서만 꺼내므로 여러 스레드가 동시에 접근할 때 발생하는 Lock Contention이 없어 속도가 매우 빠름




#### Global Run Queue
![](../05_attachments/Pasted%20image%2020260709030720.png)
- 로컬 큐가 꽉 차거나, 시스템 콜 이후 돌아온 ***G*** 들이 임시로 머무는 공유 큐
- 모든 ***P***가 접근할 수 있으므로 Lock 이 작동하여 로컬 큐보다 속도가 느림




#### netpoller

- **netpoller**는 Go runtime에서 비동기 네트워크 I/O system call을 담당하는 컴포넌트이다.
- 만약 `G`가 네트워크 I/O를 하게 되면, `G`를 실행하던 `M`은 block되는 대신, 해당 `G`를 netpoller에서 기다리게 한다. 그리고 `M`은 block되지 않고 다른 `G`를 실행한다.
- 만약 I/O가 완료되면 `G`는 준비됐음을 알린다. 이렇게 `M`을 block되지 않게 만들어 성능을 향상시킨다.

