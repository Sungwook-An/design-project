import gym
import JSSEnv
import imageio

class FIFO():
    def __init__(self):
        INSTANCE_PATH = 'instances/ta01' # job 20개, machine 15개
        self.env = gym.make('jss-v1', env_config={'instance_path': INSTANCE_PATH})
        self.env.reset()
        self.FIFO_list: list[list[int, int, int]] = []
        self.legal_machine_list: list[bool] = [True for _ in range(self.env.machines)]
        self.legal_job_list: list[bool] = [True for _ in range(self.env.jobs)]
        self.legal_FIFO_list: list[bool] = [False for _ in range(self.env.jobs)]
        self.time_until_machine_available: list[int] = [0 for _ in range(self.env.machines)]
        self.current_order_of_operation_list: list[int] = [0 for _ in range(self.env.jobs)]
        self.reward_list_after_each_operation: list[float] = []
        self.finished_step = [[0 for _ in range(self.env.machines)] for _ in range(self.env.jobs)]

    def initial_setting(self):
        for job in range(self.env.jobs):
            machine = self.env.instance_matrix[job][0][0]
            time = self.env.instance_matrix[job][0][1]
            self.FIFO_list.append([job, machine, time])
                
            if (self.legal_machine_list[machine] == True):
                self.legal_machine_list[machine] = False
                self.legal_FIFO_list[job] = True
                self.time_until_machine_available[machine] = time
        
        for i in range(len(self.FIFO_list)):
            job = self.FIFO_list[i][0]
            if (self.legal_FIFO_list[i] == True):
                self.legal_job_list[job] = False
                
    def check_minimum_time(self):
        min_time = float('inf')
        for i in range(self.env.machines):
            if (self.time_until_machine_available[i] != 0 and self.time_until_machine_available[i] <= min_time):
                min_time = self.time_until_machine_available[i]
        return min_time
    
    def reduce_time(self, machine, min_time, i):
        self.time_until_machine_available[machine] -= min_time
        self.FIFO_list[i][2] = self.time_until_machine_available[machine]
        
    def add_reward(self, job, current_order):
        if (self.finished_step[job][current_order] == 0):
            while (self.env.solution[job][self.env.todo_time_step_job[job]] != -1):
                if (self.env.next_time_step != []):
                    self.env.increase_time_step()
            _, reward, _, _ = self.env.step(job)
            self.reward_list_after_each_operation.append(reward)
            self.finished_step[job][current_order] = 1
            
    def delete_finished_op_and_add_new_op(self, machine, i, job, current_order):
        if (self.time_until_machine_available[machine] == 0):
            del self.FIFO_list[i]
        
            if (current_order < self.env.machines - 1):
                self.current_order_of_operation_list[job] += 1
                current_order = self.current_order_of_operation_list[job]
                new_job = job
                new_machine = self.env.instance_matrix[job][current_order][0]
                new_time = self.env.instance_matrix[job][current_order][1]
                self.FIFO_list.append([new_job, new_machine, new_time])
                
    def new_setting(self):
        self.legal_machine_list = [True for _ in range(self.env.machines)]
        self.legal_job_list = [True for _ in range(self.env.jobs)]
        self.legal_FIFO_list = [False for _ in range(self.env.jobs)]
        for i in range(len(self.FIFO_list)):
            job = self.FIFO_list[i][0]
            machine = self.FIFO_list[i][1]
            time = self.FIFO_list[i][2]
            if (self.legal_machine_list[machine] == True and self.legal_job_list[job] == True and self.legal_FIFO_list[i] == False):
                self.legal_machine_list[machine] = False
                self.legal_job_list[job] = False
                self.legal_FIFO_list[i] = True
                self.time_until_machine_available[machine] = time
                
    def save_gantt_chart(self):
        img = []
        fig = self.env.render().to_image()
        img.append(imageio.imread(fig))
        imageio.mimsave("ta01.gif", img)
        
    def get_makespan(self):
        start_sec = self.env.start_timestamp
        makespan = 0
        for job in range(self.env.jobs):
            last_operation = self.env.machines - 1
            finish_sec = start_sec + self.env.solution[job][last_operation] + self.env.instance_matrix[job][last_operation][1]
            if (finish_sec - start_sec > makespan):
                makespan = finish_sec - start_sec
                
        return makespan

    def iteration(self):
        self.initial_setting()
        
        while (len(self.FIFO_list) != 0):
            min_time = self.check_minimum_time()
            
            for i in range(len(self.FIFO_list) - 1, -1, -1):
                if (self.legal_FIFO_list[i] == True):
                    job = self.FIFO_list[i][0]
                    machine = self.FIFO_list[i][1]
                    current_order = self.current_order_of_operation_list[job]

                    self.reduce_time(machine, min_time, i)
                    self.add_reward(job, current_order)
                    self.delete_finished_op_and_add_new_op(machine, i, job, current_order)
             
            self.new_setting()
        self.save_gantt_chart()
        makespan = self.get_makespan()
        return self.reward_list_after_each_operation, makespan
