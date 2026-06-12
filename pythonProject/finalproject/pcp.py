#  == 조건 변수로 생산 소비 문제 ===

# import threading
# import time
# import random
#
# MAX = 30
# buffer = []
#
# # 조건변수는 반드시 mutex 필요
# # 제대로 생산자는 소비자를 소비자는 생산자를 꺠우기 위해 변수 두개 empty, fill
#
# mutex = threading.Lock()
# empty_cv = threading.Condition(mutex)  # 생산자가 자는 큐
# fill_cv = threading.Condition(mutex)  # 소비자 자는 큐
#
#
# def producer(id):
#     for i in range(50):
#         with mutex:  # 락 얻기
#
#
#             # 조건 다시 확인해야되니까 while문
#             while len(buffer) == MAX:
#                 empty_cv.wait()
#
#             # 저기 통과한 애들은 여기서 생산
#             item = f"데이터-{id}-{i}"
#             buffer.append(item)
#             print(f"[생산자 {id}] '{item}' 생산 | 현재 버퍼 크기: {len(buffer)} / {MAX}")
#
#             # fill 에 있는 소비자 꺠움
#             fill_cv.notify()
#
#             # with 블록을 빠져나가면 파이썬은 알아서 signal해준다함
#
#         # 테스트할 때 띄우려고 넣ㅇ므
#         time.sleep(random.uniform(0.01, 0.05))
#
#
# def consumer(id):
#     for i in range(50):
#         with mutex:
#
#
#             # 버퍼가 비어잇으면 fill 큐로 가서 gotosleep
#             while len(buffer) == 0:
#                 fill_cv.wait()
#
#
#
#             item = buffer.pop(0)
#             print(f"[소비자 {id}] '{item}' 소비 | 현재 버퍼 크기: {len(buffer)} / {MAX}")
#
#             # empty에 있는생산자 깨우기
#             empty_cv.notify()
#
#         # 테스트
#         time.sleep(random.uniform(0.01, 0.05))
#
#
# # 출력코드
# if __name__ == "__main__":
#     print("=== CV 사용 생산자-소비자 테스트 ===")
#     threads = []
#
#     # 생산자 소비자 둘둘
#
#     for i in range(2):
#         threads.append(threading.Thread(target=producer, args=(i,)))
#         threads.append(threading.Thread(target=consumer, args=(i,)))
#
#     for t in threads: t.start()
#     for t in threads: t.join()
#
#     print("\nProducer-Consumer (CV) 끝")



    # === 여기는 세마포어로 생산 소비 문제 ===
    # import threading
    # import time
    # import random
    #
    # from numpy.f2py.crackfortran import appenddecl
    #
    # # 버퍼 max 30
    # MAX = 30
    # buffer = []
    #
    # # 세마포어 변수 1 초기화 / empty가 맥스 / fulll 이 없는거
    # mutex = threading.Semaphore(1)
    # empty = threading.Semaphore(MAX)
    # full = threading.Semaphore(0)
    #
    #
    #
    # # 생산자 함수
    # # 버퍼가 max면 gotosleep
    # # 아니면 락 잡고 append
    # # 완료하면 full에 있는 소비자 깨우기
    #
    # def producer(id):
    #     for i in range(50):
    #         empty.acquire()  # 버퍼 빈공간일 때까지 기다림
    #         mutex.acquire()  # 뮤텍스 버퍼 권한 얻고
    #
    #         # 여기가 critical section
    #
    #         item = f"데이터-{id}-{i}"
    #         buffer.append(item)
    #         print(f"[생산자 {id}] '{item}' 생산 | 현재 버퍼 크기: {len(buffer)} / {MAX}")
    #
    #
    #         mutex.release()  # 버퍼 접근 권한 반환
    #         full.release()  # 채워진 데이터 개수 증가 (소비자 깨움)
    #
    #         time.sleep(random.uniform(0.01, 0.05))
    #
    #
    # def consumer(id):
    #     for i in range(50):
    #         full.acquire()  # 채워진 데이터가 있을 때까지 기다리기
    #         mutex.acquire()  # 버퍼에 대한 독점적 접근 권한 획득
    #
    #         # 임계 구역 (Critical Section)
    #         item = buffer.pop(0)
    #         print(f"[소비자 {id}] '{item}' 소비 | 현재 버퍼 크기: {len(buffer)} / {MAX}")
    #
    #         mutex.release()  # 버퍼 접근 권한 반환
    #         empty.release()  # 빈 공간 개수 증가 (생산자 깨움)
    #         time.sleep(random.uniform(0.01, 0.05))
    #
    #
    # # 대충 테스트 코드만
    # # 생산자 0,1  소비자 0,1 둘씩
    #
    # if __name__ == "__main__":
    #     threads = []
    #
    #     for i in range(2):
    #         threads.append(threading.Thread(target=producer, args=(i,)))
    #         threads.append(threading.Thread(target=consumer, args=(i,)))
    #
    #     for t in threads:
    #         t.start()
    #
    #     # 조인문으로 같이
    #
    #     for t in threads:
    #         t.join()
    #
    #
    #     print("Producer-Consumer 끝")


import threading
import time

# 두 개의 세마포어 선언 (초기값 1로 설정하여 뮤텍스/이진 세마포어처럼 사용)
sem_A = threading.Semaphore(1)
sem_B = threading.Semaphore(1)


def process_P():

    print("[Process P] 자원 A 요청")
    sem_A.acquire()  # 1. 자원 A 얻음

    print("[Process P] 자원 A 획득 1초 대기")

    # 데드락 유발 -> context switch Q로
    time.sleep(1)

    print("[Process P] 자원 B 요청")
    sem_B.acquire()  # P가 B를 요청하는데 이거 잡고있는 Q는 sleep

    print("[Process P] 실행 끝")

    sem_B.release()
    sem_A.release()


def process_Q():
    print("[Process Q] 자원 B 요청")
    sem_B.acquire()  # Q가 B잡고
    print("[Process Q] 자원 B 획득 1초 대기")

    time.sleep(1)

    print("[Process Q] 자원 A 요청")
    sem_A.acquire()  # 점유대기로 B잡고 있는데 A요청 근데 P가 잡고 자러감

    print("[Process Q] 실행 끝")

    sem_A.release()
    sem_B.release()


if __name__ == "__main__":
    # 두 스레드 동시 생성 및 실행
    t1 = threading.Thread(target=process_P)
    t2 = threading.Thread(target=process_Q)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("여기는 출려기 안됨")