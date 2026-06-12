import threading
import time
from typing import List


class BoundedBufferPC:

    def __init__(self, max_size: int = 30, verbose: bool = False):
        self.max_size = max_size
        self.verbose = verbose

        # 공유 자원 (버퍼의 현재 아이템 수)
        self.x = 0

        # 세마포어 및 락 설정
        # 파이썬의 Semaphore는 초깃값을 인자로 받습니다.
        self.empty = threading.Semaphore(max_size)  # 빈 슬롯 수 (초기값 MAX)
        self.full = threading.Semaphore(0)  # 채워진 슬롯 수 (초기값 0)
        self.mutex = threading.Lock()  # 상호 배제를 위한 락 (Binary Semaphore 역할)

        # Evaluation 지표 (파이썬은 기본 연산이 원자적이지 않으므로, 이 지표 측정을 위해서도 mutex를 활용합니다)
        self.produced_total = 0
        self.consumed_total = 0
        self.producer_blocked = 0
        self.consumer_blocked = 0
        self.min_x = float("inf")
        self.max_x = float("-inf")

    def produce(self, producer_id: int, iterations: int) -> None:
        for _ in range(iterations):
            # empty 세마포어가 0인지 체크하여 블록 여부 확인 (Strict하지는 않지만 자바 로직 복사)
            # 파이썬의 _value는 내부 구현체이므로 세마포어 상태 파악용으로만 참고합니다.
            if self.empty._value == 0:
                with self.mutex:
                    self.producer_blocked += 1

            self.empty.acquire()  # 빈 자리가 날 때까지 대기

            with self.mutex:  # 자바의 try-finally 블록 대신 파이썬의 context manager(with) 사용
                self.x += 1
                self.min_x = min(self.min_x, self.x)
                self.max_x = max(self.max_x, self.x)
                self.produced_total += 1
                if self.verbose:
                    print(
                        f"[Producer-{producer_id}] produce -> x={self.x} (MAX={self.max_size})"
                    )

            self.full.release()  # 소비자에게 신호 송신

    def consume(self, consumer_id: int, iterations: int) -> None:
        for _ in range(iterations):
            if self.full._value == 0:
                with self.mutex:
                    self.consumer_blocked += 1

            self.full.acquire()  # 채워진 아이템이 있을 때까지 대기

            with self.mutex:
                self.x -= 1
                self.min_x = min(self.min_x, self.x)
                self.max_x = max(self.max_x, self.x)
                self.consumed_total += 1
                if self.verbose:
                    print(
                        f"[Consumer-{consumer_id}] consume -> x={self.x} (MAX={self.max_size})"
                    )

            self.empty.release()  # 생산자에게 빈 자리 신호 송신


def run_experiment(
    num_producers: int, num_consumers: int, total_items: int
) -> None:
    pc = BoundedBufferPC(max_size=30, verbose=False)

    # 각 스레드가 반복할 횟수 계산
    iter_p = total_items // num_producers
    iter_c = total_items // num_consumers

    producers: List[threading.Thread] = []
    consumers: List[threading.Thread] = []

    start_time = time.perf_counter()

    # 생산자 스레드 생성
    for i in range(num_producers):
        t = threading.Thread(target=pc.produce, args=(i, iter_p))
        producers.append(t)

    # 소비자 스레드 생성
    for i in range(num_consumers):
        t = threading.Thread(target=pc.consume, args=(i, iter_c))
        consumers.append(t)

    # 스레드 일제히 시작
    for t in producers + consumers:
        t.start()

    # 모든 스레드가 종료될 때까지 대기
    for t in producers + consumers:
        t.join()

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    in_range = pc.min_x >= 0 and pc.max_x <= pc.max_size
    range_status = "OK" if in_range else "FAIL"
    throughput = (pc.produced_total + pc.consumed_total) / max(
        1.0, elapsed_ms / 1000.0
    )

    print(
        f"[Bounded/Sem ] P={num_producers} C={num_consumers} total={total_items} | "
        f"time={elapsed_ms:4.0f}ms | produced={pc.produced_total:<6} consumed={pc.consumed_total:<6} final x={pc.x:<4} | "
        f"range x=[{pc.min_x},{pc.max_x}] (0<=x<={pc.max_size} : {range_status}) | "
        f"producerBlocked={pc.producer_blocked:<6} consumerBlocked={pc.consumer_blocked:<6} | "
        f"throughput={throughput:.1f} ops/s"
    )


if __name__ == "__main__":
    print(
        "=== Producer-Consumer : Bounded Buffer (Semaphore, MAX=30) ==="
    )
    configs = [
        [1, 1, 4000],
        [2, 2, 4000],
        [4, 1, 4000],
        [1, 4, 4000],
        [4, 4, 4000],
    ]

    for cfg in configs:
        run_experiment(cfg[0], cfg[1], cfg[2])