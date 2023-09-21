from fifo import *
import numpy as np

fifo_result = FIFO()
rl, makespan = fifo_result.iteration()
reward = np.array(rl).sum()

reward = reward.round(3)
makespan = makespan.round(3)

print(reward)       # 10.626
print(makespan)     # 1468.0 sec

