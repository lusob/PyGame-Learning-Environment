import numpy as np
import ipdb
from cStringIO import StringIO
from . import base
from .. import tiles

class MultiGoals(base.Scenario):

    def __init__(self, rng):
        block_strings = ["AG", "WA", "BU"] #blocks we use
        base.Scenario.__init__(self, rng, block_strings)    

    def generate(self):
        self.goals = {}
        self.goals_order = []
        self.next_goal = 0
        
        w, h = self.rng.uniform(self._min, self._max + 1, size=(2)).astype(int)
        self.map_str = np.zeros([h, w], dtype=object)
        locs = np.where(self.map_str == 0)
        self.map_str[locs] = self.EMPTY_TILE
        
        pos_h, pos_w = self.rng.randint(0, high=np.min([w,h])-1, size=(2))
        while self.map_str[pos_h, pos_w] != self.EMPTY_TILE:
            pos_w = self.rng.randint(side[0], high=side[1])
            pos_h = self.rng.randint(0, high=h-1)

        #random side for agent
        self.map_str[pos_h, pos_w] = "AG"
        
        #select a column as the wall
        num_goals = self.rng.randint(2, high=6)
        num_active = self.rng.randint(1, high=num_goals)
        num_placed = 0
        while num_placed < num_goals:
            pos_h, pos_w = self.rng.randint(0, high=np.min([w,h])-1, size=(2))
            while self.map_str[pos_h, pos_w] != self.EMPTY_TILE or self.map_str[pos_h, pos_w] == "AG" or self._blocking(pos_w, pos_h):

                pos_w = self.rng.randint(0, high=w-1)
                pos_h = self.rng.randint(0, high=h-1)
            
            self.map_str[pos_h, pos_w] = "GOT_%s" % num_placed
            self.block_strings.extend(["GOT_%s" % num_placed])
            num_placed += 1

        selected_goals = self.rng.choice(np.arange(num_goals), num_active, replace=False)
        self.goals_order = [ str(i) for i in selected_goals ]
        
        #make 20% of remaining blocks randomly water or unmoveable blocks
        empty_blocks = len(np.where( self.map_str == self.EMPTY_TILE )[0])
        num_blocks = empty_blocks*self.percent
        num_placed = 0
        while num_placed < num_blocks:
            tries = 0
            while self._occupied(pos_w, pos_h) or self._blocking(pos_w, pos_h):
                pos_w = self.rng.randint(0, high=w-1)
                pos_h = self.rng.randint(0, high=h-1)
                tries += 1

                if tries > empty_blocks:
                    break
            
            if tries > empty_blocks:
                break 

            block = self.rng.choice(["WA", "BU"])
            self.map_str[ pos_h, pos_w ] = block
            num_placed += 1

    def _blocking(self, pos_w, pos_h):
        #if a block were placed in pos_w, pos_h would it stop the level from being completed?
        pos = np.array([pos_h, pos_w])
        pos = np.array([ [1,0], [-1, 0], [0, 1], [0, -1] ]) + pos

        h = np.clip(pos[:, 0], 0, self.map_str.shape[0]-1) #the heights
        w = np.clip(pos[:, 1], 0, self.map_str.shape[1]-1)
        area = self.map_str[(h, w)].tolist()
       
        if "BU" in area: #we dont want too many blocks near e/o
            return True

        for sq in area:
            if "GOT_" in sq:
                return True

        #checks if this would block the player or door.
        return False

    def info(self):
        info_str = "Info: Visit the goals in the following order "
        goals_str = [ "Goal #%s" % i for i in self.goals_order ]
        if len(goals_str) > 1:
            goals = ", ".join(goals_str[:-1])
            goals += " and " + goals_str[-1]
        else:
            goals = ", ".join(goals_str)

        return_str = info_str + goals
        return return_str + ".\n"

    def setup(self, tile_objs):
        for t in tile_objs:
            if isinstance(t, tiles.GoalToggle) and t.toggles in self.goals_order:
                t.toggle()
                self.goals[t.toggles] = t

    def is_complete(self):
        num_completed = 0
        for i in range(len(self.goals_order)):
            current_goal = self.goals[self.goals_order[i]].visited
            if i == self.next_goal and current_goal:
                self.next_goal += 1
                num_completed += 1
                #has the next goal been completed?
            elif i < self.next_goal and current_goal:
                num_completed += 1
            else: #clear all others
                if current_goal: #only if its been visited before.
                    self.goals[self.goals_order[i]].visited = False
                    self.goals[self.goals_order[i]].toggle()
                
        if num_completed == len(self.goals_order):
            return True
    
        return False