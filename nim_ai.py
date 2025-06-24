import random
from nim_game import Nim

class NimAI:
    def __init__(self, alpha=0.5, epsilon=0.1):
        self.q = {}
        self.alpha = alpha
        self.epsilon = epsilon

    def get_q_value(self, state, action):
        state = tuple(state)
        action = tuple(action)
        return self.q.get((state, action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        state = tuple(state)
        action = tuple(action)
        new_q = old_q + self.alpha * (reward + future_rewards - old_q)
        self.q[(state, action)] = new_q

    def best_future_reward(self, state):
        actions = Nim.available_actions(state)
        if not actions:
            return 0
        return max(self.get_q_value(state, action) for action in actions)

    def update(self, old_state, action, new_state, reward):
        old_q = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old_q, reward, best_future)

    def choose_action(self, state, epsilon=True):
        actions = list(Nim.available_actions(state))
        if epsilon and random.random() < self.epsilon:
            return random.choice(actions)
        q_values = [(action, self.get_q_value(state, action)) for action in actions]
        return max(q_values, key=lambda x: x[1])[0]