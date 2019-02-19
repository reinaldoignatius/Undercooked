class BlackboardSystem():

    def __init__(self, number_of_agents):
        self.__number_of_agents = number_of_agents
        self.writings = {}
        for i in range(number_of_agents):
            self.writings["chef_%d" % (i + 1)] = []

    def write(self, agent_name, writing):
        if not self.writings[agent_name]:
            self.writings[agent_name].append(writing)
        else:
            if self.writings[agent_name][-1] != writing: 
                self.writings[agent_name].append(writing)
    
    def read_recent_writings(self, agent_name):
        recent_writings = {}
        for writer in self.writings:
            if writer != agent_name:
                if self.writings[writer]:
                    recent_writings[writer] = self.writings[writer][-1]
                else:
                    recent_writings[writer] = ''
        return recent_writings