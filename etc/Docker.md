![](../img/Pasted%20image%2020260922121934.png)
> [출처](https://docs.docker.com/get-started/overview/)

![](https://blog.kakaocdn.net/dna/biCkg5/btsGqJkflEN/AAAAAAAAAAAAAAAAAAAAAJB6N_8R7_WEcdl4ZWVqfnEYH1QwNE7AH-6W1B4SKBCj/img.jpg?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1790780399&allow_ip=&allow_referer=&signature=hA29WYFkIZT%2FlSV%2FsVDsCKootbw%3D)
> [출처](https://junesker.tistory.com/88)

기존 가상 머신(Virtual Machine)은 하이퍼바이저를 이용해 호스트 운영체제에 여러 개의 운영체제를 생성하고 각 운영체제는 가상 머신 단위로 구별된다. 그러나 이는 시스템 자원을 가상화하고 독립된 공간을 생성하며 하이퍼바이저를 반드시 거쳐야하기 때문에 오버헤드가 발생한다. 

도커 컨테이너(Docker Container)는 가상화된 공간을 생성하기 위해 chroot, namespace, cgroup 등의 Linux 자체 기능을 사용하여 프로세스 단위의 격리 환경을 만들기 때문에 기존 VM처럼 하이퍼바이저를 사용하지 않는다. 컨테이너에서 필요한 커널을 공유해서 사용하고 컨테이너 안에는 단지 어플리케이션을 구동하는데 필요한 라이브러리 및 실행 파일만 존재하기 때문에 컨테이너를 이미지로 만들었을 때 이미지의 용량 또한 가상머신에 비해 줄어든다. 따라서 가상 머신에 비해 이미지의 생성, 배포가 빠르고 오버헤드 또한 적다.


*참고자료*
- *https://docs.docker.com/get-started/docker-overview/*
- *https://junesker.tistory.com/88*