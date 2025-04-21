import os
tree_files = "mcts/mcts_data/multi_turn_jailbreak/rollout3/4-steps-request/trees/"
if not os.path.exists(tree_files):
    os.mkdir(tree_files)