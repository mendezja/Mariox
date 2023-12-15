#using ppo clip alg as described in https://spinningup.openai.com/en/latest/algorithms/ppo.html



import torch
from torch.distributions import Categorical

from modules.rl.neural import MarioNet
import random
import numpy as np

from torch.optim import Adam
from collections import deque


class MarioPPO:
    def __init__(self, state_dim, action_dim, save_dir, env, checkpoint=None):

        self.env=env
        self.action_set = env.action_set
        # Assign state and action dimensions, create memory buffer
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.memory = deque(maxlen=100000)
        #self.batch_size = 32

        #some basic hyper paramaters
        self.timesteps_per_batch = 4800
        self.max_timesteps_per_episode = 1600
        self.gamma = .99
        self.epochs = 10
        self.n_updates_per_iteration = 5
        self.lr = 0.005
        self.clip = 0.2                                


        #init actor and critic nets
        self.actor = MarioNet(self.state_dim, self.action_dim)
        self.critic = MarioNet(self.action_dim,1)

        #optimizers for actor and critic
        self.actor_optim = Adam(self.actor.parameters(), lr=self.lr)
        self.critic_optim = Adam(self.critic.parameters(), lr=self.lr)

        #making the distributions
        self.cov_var = torch.full(size=(self.action_dim,), fill_value=0.5)
  
        # Create the covariance matrix f
        self.cov_mat = torch.diag(self.cov_var)

        # This logger will help us with printing out summaries of each iteration
        self.logger = {
			#'delta_t': time.time_ns(),
			't_so_far': 0,          # timesteps so far
			'i_so_far': 0,          # iterations so far
			'batch_lens': [],       # episodic lengths in batch
			'batch_rews': [],       # episodic returns in batch
			'actor_losses': [],     # losses of actor network in current iteration
		}

    def learn(self, total_timesteps):
       

        print(f"Learning... Running {self.max_timesteps_per_episode} timesteps per episode, ", end='')
        print(f"{self.timesteps_per_batch} timesteps per batch for a total of {total_timesteps} timesteps")
        t_so_far = 0 # Timesteps simulated so far
        i_so_far = 0 # Iterations ran so far
		
        while t_so_far < total_timesteps:              
            # increment t_so_far somewhere below
            # collect batches from trajectory data

            #figure out shape of lists in a bit

            batch_obs = []             # batch observations
            batch_acts = []            # batch actions
            batch_log_probs = []       # log probs of each action
            batch_rews = []            # batch rewards
            batch_rtgs = []            # batch rewards-to-go
            batch_lens = []            # episodic lengths in batch

            #run until we hit self.timesteps_per_batch

            t = 0 
            while t < self.timesteps_per_batch:
            # Rewards this episode
                ep_rews = []
                obs = self.env.reset()
                done = False
                for ep_t in range(self.max_timesteps_per_episode):

                    # Increment timesteps ran this batch so far
                    t += 1
                    # Collect observation
                    batch_obs.append(obs)

                    mean = self.actor(obs, "online", True)
                    # create our normal distribution
                   
                    dist = Categorical(mean)
                    # sample an action from the distribution and get its log prob
                    print(dist)
                    action = dist.sample()
                    #print(action)
                    log_prob = dist.log_prob(action)

                    #Now we have luigi just do a random action
                    #for future, could do selfplay!
                    luigi_action = self.action_set[random.randint(0, len(self.action_set) - 1)]
                    #print(luigi_action)
                    # return the sampled action and the log prob of that action                    
                    action, logprob = action.detach().numpy(), log_prob.detach()

                    obs, reward, done = self.env.step([action, luigi_action])
                
                    # Collect reward, action, and log prob
                    ep_rews.append(reward[1])
                    print(type(action))
                    batch_acts.append(action)
                    batch_log_probs.append(log_prob)
                    if done:#done:
                        break
                # collect episodic length and rewards
                batch_lens.append(ep_t + 1) # plus 1 because timestep starts at 0
                batch_rews.append(ep_rews) 

            #computing rewards to go

            for ep_rews in reversed(batch_rews):

                discounted_rew = 0

                #go through all rews
                # switched to reverse cause forgot it went from end bc of gamma
                for rew in reversed(ep_rews):
                    #print(rew)
                    discounted_rew = discounted_rew * self.gamma + rew
                    batch_rtgs=[discounted_rew] + batch_rtgs


        # reshape as tensors
            print(batch_acts)

            batch_obs = torch.tensor(batch_obs, dtype=torch.float)
            batch_acts = torch.tensor(batch_acts, dtype=torch.float)
            batch_log_probs = torch.tensor(batch_log_probs, dtype=torch.float) 
            batch_rtgs = torch.tensor(batch_rtgs, dtype=torch.float)

            # Logging timesteps so far and iterations so far
            self.logger['t_so_far'] = t_so_far
            self.logger['i_so_far'] = i_so_far
            
            t_so_far += np.sum(batch_lens)

			# Increment the number of iterations
            i_so_far += 1

            #alreaddy have q vals, need V vals 
            print(batch_obs)
            #squeeze to make it right orientation
            vals = self.critic(batch_obs, "online", True).squeeze()

            # now we can calc advantage
            adv = batch_rtgs - vals.detach()

            #update policies!
            for _ in range(self.epochs):
                #ratio first
                #log prob of actions, similar to log prob of qvals im guessing
                mean = self.actor(obs, "online", True)
                # create our normal distribution
                dist = Categorical(self.cov_mat)
                # sample an action from the distribution and get its log prob
                action = dist.sample()
                #had to change to batch_acts to get same size
                log_prob = dist.log_prob(batch_acts)

                #log prob is easy cause we can just use subtraction instead of division
                ratios = torch.exp(curr_log_probs - batch_log_probs)

                #surr losses
                surr1 = ratios * adv
                #This is where the clipping comes in
                surr2 = torch.clamp(ratios, 1 - self.clip, 1 + self.clip) * A_k

                # Calculate actor and critic losses.
                actor_loss = (-torch.min(surr1, surr2)).mean()
                critic_loss = nn.MSELoss()(vals, batch_rtgs)


                # Calculate gradients and perform backward propagation for actor network
                self.actor_optim.zero_grad()
                actor_loss.backward(retain_graph=True)
                self.actor_optim.step()

				# Calculate gradients and perform backward propagation for critic network
                self.critic_optim.zero_grad()
                critic_loss.backward()
                self.critic_optim.step()

                # Log actor loss
                self.logger['actor_losses'].append(actor_loss.detach())

			# Print a summary of our training so far
            self._log_summary()

			# Save our model if it's time
            if i_so_far % self.save_freq == 0:
                torch.save(self.actor.state_dict(), './ppo_actor.pth')
                torch.save(self.critic.state_dict(), './ppo_critic.pth')

    def _log_summary(self):

        # Calculate logging values. I use a few python shortcuts to calculate each value
        # without explaining since it's not too important to PPO; feel free to look it over,
        # and if you have any questions you can email me (look at bottom of README)
       # delta_t = self.logger['delta_t']
        #self.logger['delta_t'] = time.time_ns()
        #delta_t = (self.logger['delta_t'] - delta_t) / 1e9
        #delta_t = str(round(delta_t, 2))

        t_so_far = self.logger['t_so_far']
        i_so_far = self.logger['i_so_far']
        avg_ep_lens = np.mean(self.logger['batch_lens'])
        avg_ep_rews = np.mean([np.sum(ep_rews) for ep_rews in self.logger['batch_rews']])
        avg_actor_loss = np.mean([losses.float().mean() for losses in self.logger['actor_losses']])

        # Round decimal places for more aesthetic logging messages
        avg_ep_lens = str(round(avg_ep_lens, 2))
        avg_ep_rews = str(round(avg_ep_rews, 2))
        avg_actor_loss = str(round(avg_actor_loss, 5))

        # Print logging statements
        print(flush=True)
        print(f"-------------------- Iteration #{i_so_far} --------------------", flush=True)
        print(f"Average Episodic Length: {avg_ep_lens}", flush=True)
        print(f"Average Episodic Return: {avg_ep_rews}", flush=True)
        print(f"Average Loss: {avg_actor_loss}", flush=True)
        print(f"Timesteps So Far: {t_so_far}", flush=True)
       # print(f"Iteration took: {delta_t} secs", flush=True)
        print(f"------------------------------------------------------", flush=True)
        print(flush=True)

        # Reset batch-specific logging data
        self.logger['batch_lens'] = []
        self.logger['batch_rews'] = []
        self.logger['actor_losses'] = []       

        