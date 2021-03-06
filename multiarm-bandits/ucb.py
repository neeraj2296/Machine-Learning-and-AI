################################################################################
#                                                                              #
# Statistical Machine Learning & AI                                            #
#                                                                              #
# Problem:  Multi-arm bandits                                                  #
#                                                                              #
# Author:   Anubhav Singh                                                      #
#                                                                              #
################################################################################

from mab import MAB
import numpy as np

def argmax_rand(a):
    """
    Arguments
    =========
    a : numpy float array, 1-D of length 'narms'

    Returns:
    ========
    index : int
        Randomly pick an index from the set of
        indices corresponding to a's max value.
    """
    return np.random.choice(np.flatnonzero(a == a.max()))

class UCB(MAB):
    """
    Upper Confidence Bound (UCB) multi-armed bandit

    Arguments
    =========
    narms : int
        number of arms

    rho : float
        positive real explore-exploit parameter

    Q0 : float, optional
        initial value for the arms
    """

    def __init__(self, narms, rho, Q0=np.inf):
        """
        Initialize the instance variables
        """

        self.narms = narms
        self.Q0 = Q0
        self.rho = rho
        self.Q = np.zeros(narms)
        self.Q_mu = np.full(narms, Q0)
        self.arm_at_t = {}
        self.reward_at_t = []
        self.num_times_arm = {}

    def play(self, tround, context=None):
        """
        Play a round

        Arguments
        =========
        tround : int
            positive integer identifying the round

        context : 1D float array, shape (self.ndims * self.narms),
        optional context given to the arms

        Returns
        =======
        arm : int
            the positive integer arm id for this round
        """

        # Rejects multiple play calls for same round number
        # - by resetting the counters updated by previous call.
        if tround in self.arm_at_t.keys():
            tround_repeat = True
            self.num_times_arm[self.arm_at_t[tround]]-=1
        else:
            tround_repeat = False

        # Random tie-break against all index corresponding to max value of Q
        self.arm_at_t[tround] = argmax_rand(self.Q)

        # Update the counter for number of times an arm was pulled
        self.num_times_arm[self.arm_at_t[tround]] \
            = self.num_times_arm.setdefault(self.arm_at_t[tround],0)+1

        return self.arm_at_t[tround]+1

    def update(self, arm, reward, context=None):
        """
        Updates the internal state of the MAB after a play

        Arguments
        =========
        arm : int
            a positive integer arm id in {1, ..., self.narms}

        reward : float
            reward received from arm

        context : 1D float array, shape (self.ndims * self.narms), optional
            context given to arms
        """

        arm-=1

        self.reward_at_t.append(reward)

        self.Q_mu[arm] \
            = (((self.Q_mu[arm] \
                 *(self.num_times_arm[arm]-1))+reward)/self.num_times_arm[arm])
        #print((self.rho*np.log10(len(self.arm_at_t)+1)),(self.num_times_arm[arm]))
        for a  in self.num_times_arm.keys():
            if self.num_times_arm[a]>0:
                self.Q[a] \
                    = np.sqrt(self.rho*np.log10 \
                              (len(self.arm_at_t)+1)/self.num_times_arm[a]) \
                                + self.Q_mu[a]
