import aiofiles
from core.bnbchain import CheckEligible
from core.utils import random_line, logger
import asyncio


async def Checker(thread):
    logger.info(f"Thread {thread} | Started work")
    while True:
        act = await random_line('data/accounts.txt')
        if not act: break

        if '::' in act:
            private_key, proxy = act.split('::')
        else:
            private_key = act
            proxy = None

        bnbchain = CheckEligible(key=private_key, proxy=proxy)

        if await bnbchain.login():
            level1, level2 = await bnbchain.check_eligible()

            if level1 or level2:
                logger.success(f"Thread {thread} | Eligible for level(s): {1 if level1 else ''} {2 if level2 else ''}")

                async with aiofiles.open('data/eligible.txt', 'a', encoding='utf-8') as f:
                    await f.write(f'{bnbchain.web3_utils.acct.address}\n')
            else:
                logger.warning(f"Thread {thread} | Not eligible")

        await bnbchain.logout()

    logger.info(f"Thread {thread} | Finished work")


async def main():
    print("Checker's author: https://t.me/ApeCryptor")

    thread_count = int(input("Input count of threads: "))

    tasks = []
    for thread in range(1, thread_count+1):
        tasks.append(asyncio.create_task(Checker(thread)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
