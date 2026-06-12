import threading
import time
import random

MAX = 30
buffer = []

# 조건변수는 반드시 mutex 필요
# 제대로 생산자는 소비자를 소비자는 생산자를 꺠우기 위해 변수 두개 empty, fill

mutex = threading.Lock()
empty_cv = threading.Condition(mutex)  # 생산자가 자는 큐
fill_cv = threading.Condition(mutex)  # 소비자 자는 큐


def producer(id):
    for i in range(50):
        with mutex:  # 락 얻기


            # 조건 다시 확인해야되니까 while문
            while len(buffer) == MAX:
                empty_cv.wait()

            # 저기 통과한 애들은 여기서 생산
            item = f"데이터-{id}-{i}"
            buffer.append(item)
            print(f"[생산자 {id}] '{item}' 생산 | 현재 버퍼 크기: {len(buffer)} / {MAX}")

            # fill 에 있는 소비자 꺠움
            fill_cv.notify()

            # with 블록을 빠져나가면 파이썬은 알아서 signal해준다함

        # 테스트할 때 띄우려고 넣ㅇ므
        time.sleep(random.uniform(0.01, 0.05))


def consumer(id):
    for i in range(50):
        with mutex:


            # 버퍼가 비어잇으면 fill 큐로 가서 gotosleep
            while len(buffer) == 0:
                fill_cv.wait()



            item = buffer.pop(0)
            print(f"[소비자 {id}] '{item}' 소비 | 현재 버퍼 크기: {len(buffer)} / {MAX}")

            # empty에 있는생산자 깨우기
            empty_cv.notify()

        # 테스트
        time.sleep(random.uniform(0.01, 0.05))


# 출력코드
if __name__ == "__main__":
    print("=== CV 사용 생산자-소비자 테스트 ===")
    threads = []

    # 생산자 소비자 둘둘

    for i in range(2):
        threads.append(threading.Thread(target=producer, args=(i,)))
        threads.append(threading.Thread(target=consumer, args=(i,)))

    for t in threads: t.start()
    for t in threads: t.join()

    print("\nProducer-Consumer (CV) 끝")