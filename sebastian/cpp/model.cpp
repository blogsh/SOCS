#include <vector>
#include <algorithm>
#include <random>
#include <Eigen/Dense>
#include <iostream>

float frand() {
	return (float)rand() / (float)RAND_MAX;
}

struct Agent {
	enum Type { PREDATOR, PREY } type;
	Eigen::Vector2i pos;
};

struct Params {
	Eigen::MatrixXi terrain;

	float migrationRate;
	float growthRate;
	float deathRate;

	float initialPreyRate;
	float initialPredatorRate;
};

struct Model {
	Params& mParams;
	Eigen::MatrixXi& mTerrain;

	int mSizeX, mSizeY, mSizeI;

	std::vector<Agent*>* mLattice;
	Eigen::MatrixXi mPreys;
	Eigen::MatrixXi mPredators;

	Model(Params params) :
		mParams(params), mTerrain(params.terrain) 
	{
		mSizeX = mTerrain.rows();
		mSizeY = mTerrain.cols();
		mSizeI = mSizeX * mSizeY;

		mPreys = Eigen::MatrixXi::Zero(mSizeX, mSizeY);
		mPredators = Eigen::MatrixXi::Zero(mSizeX, mSizeY);
	
		mLattice = new std::vector<Agent*>[mSizeX * mSizeY];
	
		initialize();
	}

	int index(const Eigen::Vector2i& pos) {
		return pos[0] + pos[1] * mSizeX;
	}

	int posx(int index) {
		return index % mSizeX;
	}

	int posy(int index) {
		return index % mSizeX;
	}

	void normalize(Eigen::Vector2i& pos) {
		if (pos[0] < mSizeX) pos[0] += mSizeX;
		if (pos[0] >= mSizeX) pos[0] -= mSizeX;
		if (pos[1] < mSizeY) pos[1] += mSizeY;
		if (pos[1] >= mSizeY) pos[1] -= mSizeY;
	}

	void move(Agent* agent, const Eigen::Vector2i& pos) {
		if (agent->type == Agent::PREDATOR) {
			mPredators(agent->pos[0], agent->pos[1]) -= 1;
			mPredators(pos[0], pos[1]) += 1;
		} else {
			mPreys(agent->pos[0], agent->pos[1]) -= 1;
			mPreys(pos[0], pos[1]) += 1;
		}

		std::vector<Agent*>& point = mLattice[index(agent->pos)];
		std::vector<Agent*>::iterator it = std::find(point.begin(), point.end(), agent);

		assert(it != point.end());

		point.erase(it);
		mLattice[index(pos)].push_back(agent);
		agent->pos = pos;
	}

	void transform(Agent* agent) {
		if (agent->type == Agent::PREY) {
			mPreys(agent->pos[0], agent->pos[1]) -= 1;
			mPredators(agent->pos[0], agent->pos[1]) += 1;
			agent->type = Agent::PREDATOR;
		}
	}

	void create(const Eigen::Vector2i& pos, Agent::Type type) {
		Agent* agent = new Agent;
		agent->type = type;
		agent->pos = pos;

		mLattice[index(pos)].push_back(agent);

		if (type == Agent::PREDATOR) {
			mPredators(pos[0], pos[1]) += 1;
		} else {
			mPreys(pos[0], pos[1]) += 1;
		}
	}

	void remove(Agent* agent) {
		if (agent->type == Agent::PREDATOR) {
			mPredators(agent->pos[0], agent->pos[1]) -= 1;
		} else {
			mPreys(agent->pos[0], agent->pos[1]) -= 1;
		}

		std::vector<Agent*>& point = mLattice[index(agent->pos)];
		std::vector<Agent*>::iterator it = std::find(point.begin(), point.end(), agent);

		delete *it;
		point.erase(it);
	}

	~Model() {
		std::vector<Agent*>::iterator ai;
		std::vector<Agent*>::iterator aend;

		for (int i = 0; i < mSizeI; i++) {
			ai = mLattice[i].begin();
			aend = mLattice[i].end();

			for (; ai != aend; ai++) {
				delete *ai;
			}
		}

		delete[] mLattice;
	}

	/**
	 * Initialize map according to initial rates
	 */
	void initialize() {
		std::vector<Eigen::Vector2i> all;

		for (int x = 0; x < mSizeX; x++) {
			for (int y = 0; y < mSizeY; y++) {
				if (mTerrain(x, y) > 0) {
					all.push_back(Eigen::Vector2i(x, y));
				}
			}
		}

		// Initiate predators

		std::random_shuffle(all.begin(), all.end());

		int initial = (int)( (float)all.size() * mParams.initialPredatorRate );
		
		std::for_each(
			all.begin(), all.begin() + initial, 
			std::bind(&Model::create, this, std::placeholders::_1, Agent::PREDATOR)
		);

		// Initial preys

		std::random_shuffle(all.begin(), all.end());

		initial = (int)( (float)all.size() * mParams.initialPreyRate );

		std::for_each(
			all.begin(), all.begin() + initial, 
			std::bind(&Model::create, this, std::placeholders::_1, Agent::PREY)
		);
	}

	void neighbors(std::vector<Eigen::Vector2i>& positions, const Eigen::Vector2i& pos) {
		positions.clear();
		
		static Eigen::Vector2i r1 = Eigen::Vector2i(1, 0);
		static Eigen::Vector2i r2 = Eigen::Vector2i(-1, 0);
		static Eigen::Vector2i r3 = Eigen::Vector2i(0, 1);
		static Eigen::Vector2i r4 = Eigen::Vector2i(0, -1);

		positions.push_back(pos + r1);
		positions.push_back(pos + r2);
		positions.push_back(pos + r3);
		positions.push_back(pos + r4);

		std::for_each(
			positions.begin(), positions.end(),
			std::bind(&Model::normalize, this, std::placeholders::_1)
		);
	}

	bool is_not_within(const Eigen::Vector2i& pos, int area) {
		return mTerrain(pos[0], pos[1]) != area;
	}

	bool is_prey(const Eigen::Vector2i& pos) {
		return mPreys(pos[0], pos[1]) > 0;
	}

	void step() {
		// Movement

		std::vector<Agent*>::iterator ai;
		std::vector<Agent*>::iterator aend;
		Agent* agent;

		std::vector<Eigen::Vector2i> positions;
		std::vector<Eigen::Vector2i>::iterator pi = positions.begin();
		std::vector<Eigen::Vector2i>::iterator pend = positions.end();

		for (int i = 0; i < mSizeI; i++) {
			std::vector<Agent*> buffer(mLattice[i].size());
			std::copy(mLattice[i].begin(), mLattice[i].end(), buffer.begin());
			
			ai = buffer.begin();
			aend = buffer.end();

			for(; ai != aend; ai++) {
				agent = *ai;

				neighbors(positions, agent->pos);
				pi = positions.begin();
				pend = positions.end();

				if (agent->type == Agent::PREY || !(frand() < mParams.migrationRate)) {
					pend = std::remove_if(pi, pend, std::bind(&Model::is_not_within, this, std::placeholders::_1, mTerrain(agent->pos[0], agent->pos[1])));
				}

				if (agent->type == Agent::PREY) {
					pend = std::remove_if(pi, pend, std::bind(&Model::is_prey, this, std::placeholders::_1));
				}

				if (pi != pend) {
					std::random_shuffle(pi, pend);
					move(agent, *pi);
				}
			}
		}

		// Predators eat preys

		for (int i = 0; i < mSizeI; i++) {
			if (mPreys(posx(i), posy(i)) == 0) continue;
			if (mPredators(posx(i), posy(i)) == 0) continue;

			ai = mLattice[i].begin();
			aend = mLattice[i].end();

			for (; ai != aend; ai++) {
				agent = *ai;

				if (agent->type == Agent::PREY) {
					transform(agent);
				}
			}
		}

		// Prey is born 
		for (int x = 0; x < mSizeX; x++) {
			for (int y = 0; y < mSizeY; y++) {
				if (mPreys(x,y) > 0) continue;
				if (mTerrain(x,y) < 1) continue;

				if (frand() < mParams.growthRate) {
					create(Eigen::Vector2i(x, y), Agent::PREY);
				}
			}
		}

		// Predators die 
		std::vector<Agent*> buffer;

		for (int i = 0; i < mSizeI; i++) {
			ai = mLattice[i].begin();
			aend = mLattice[i].end();

			for (; ai != aend; ai++) {
				agent = *ai;

				if (agent->type == Agent::PREDATOR && frand() < mParams.deathRate) {
					buffer.push_back(agent);
				}
			}
		}

		std::for_each(
			buffer.begin(), buffer.end(), 
			std::bind(&Model::remove, this, std::placeholders::_1)
		);
	}
};

int main(int argc, char* argv[]) {
	srand(time(0));

	Params params;

	params.migrationRate = 0.0;
	params.growthRate = 0.1;
	params.deathRate = 0.02;

	params.initialPreyRate = 0.05;
	params.initialPredatorRate = 0.05;

	Eigen::MatrixXi area1 = Eigen::MatrixXi::Constant(5, 5, 1);
	Eigen::MatrixXi area2 = Eigen::MatrixXi::Constant(5, 5, 2);
	Eigen::MatrixXi area3 = Eigen::MatrixXi::Constant(5, 5, 3);
	Eigen::MatrixXi area4 = Eigen::MatrixXi::Constant(5, 5, 4);

	Eigen::MatrixXi terrain(5, 4 * 5);
	terrain << area1, area2, area3, area4;

	params.terrain = terrain;

	const int T = 2000;
	const int K = 100;

	std::vector<int> nsum(T);
	for (int t = 0; t < T; t++) nsum[t] = 0;

	for (int k = 0; k < K; k++) {
		Model model(params);
		
		for (int t = 0; t < T; t++) {
			if (model.mPredators.sum() > 0) {
				nsum[t] += 1;
			} else {
				break;
			}

			model.step();
		}

		std::cout << (float)nsum[T-1] / (float)nsum[0] << std::endl;
	}

	return 1;
}
