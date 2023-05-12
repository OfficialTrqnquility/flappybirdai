from game import Game
import neat
import os
import pickle
import visualize

def runGame():
    Game().run()


def runTest():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    with open("winner.pkl", "rb") as f:
        genome = pickle.load(f)

    net = neat.nn.FeedForwardNetwork.create(genome, config)

    nets = [(1, net)]
    Game(nets).run()



def train():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    #p = neat.Checkpointer.restore_checkpoint("checkpoints/neat-checkpoint-20")
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    checkpointer = neat.Checkpointer(generation_interval=1, filename_prefix="checkpoints/neat-checkpoint-")
    #p.add_reporter(checkpointer)

    winner = p.run(eval_genomes)

    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)

    print('\nBest genome:\n{!s}'.format(winner))


def eval_genomes(genomes, config):
    nets = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append((genome_id, net))

    results = Game(nets, True).run()

    for genome_id, genome in genomes:
        for result in results:
            if result[0] == genome_id:
                genome.fitness = result[1]
                break


if __name__ == '__main__':
    runGame()
