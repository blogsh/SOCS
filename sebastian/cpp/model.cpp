#include <vector>
#include <algorithm>
#include <random>
#include <Eigen/Dense>
#include <Eigen/StdVector>
#include <iostream>
#include <sstream>
#include <boost/thread.hpp>
#include "include/threadpool.hpp"
#include <boost/thread/mutex.hpp>
#include <fstream>

#define GLFW_INCLUDE_GLU
#include <GLFW/glfw3.h>

EIGEN_DEFINE_STL_VECTOR_SPECIALIZATION(Eigen::Vector2i)

float frand() {
	return (float)rand() / (float)RAND_MAX;
}

struct Agent {
	enum Type { PREDATOR, PREY } type;
	Eigen::Vector2i pos;
	int starvationTime;
};

struct Params {
	Eigen::MatrixXi terrain;

	float migrationRate;
	float movementRate;
	int starvationTime;

	float preyBirthRate;
	float predatorBirthRate;

	float initialPreyCount;
	float initialPredatorCount;
};

struct Model {
	Params& mParams;
	Eigen::MatrixXi mTerrain;

	int mSizeX, mSizeY, mSizeI;

	std::vector<Agent*> mLattice;
	Eigen::MatrixXi mPreys;
	Eigen::MatrixXi mPredators;

	std::vector<int> mIndices;

	Model(Params params) :
		mParams(params), mTerrain(params.terrain) 
	{
		mSizeX = mTerrain.rows();
		mSizeY = mTerrain.cols();
		mSizeI = mSizeX * mSizeY;

		mLattice = std::vector<Agent*>(mSizeI);
		mIndices.clear();

		for (int i = 0; i < mSizeI; i++) {
			mIndices.push_back(i);
			mLattice[i] = 0;
		}

		mPreys = Eigen::MatrixXi::Zero(mSizeX, mSizeY);
		mPredators = Eigen::MatrixXi::Zero(mSizeX, mSizeY);
	
		mTerrain = mParams.terrain;
	
		initialize();
	}

	int index(const Eigen::Vector2i& pos) {
		return pos[0] + pos[1] * mSizeX;
	}

	int posx(int index) {
		return index % mSizeX;
	}

	int posy(int index) {
		return index / mSizeX;
	}

	void move(Agent* agent, const Eigen::Vector2i& pos) {
		assert(mLattice[index(pos)] == 0);

		if (agent->type == Agent::PREDATOR) {
			mPredators(agent->pos[0], agent->pos[1]) -= 1;
			mPredators(pos[0], pos[1]) += 1;
		} else {
			mPreys(agent->pos[0], agent->pos[1]) -= 1;
			mPreys(pos[0], pos[1]) += 1;
		}

		mLattice[index(agent->pos)] = 0;
		mLattice[index(pos)] = agent;
		agent->pos = pos;
	}

	void create(const Eigen::Vector2i& pos, Agent::Type type) {
		Agent* agent = new Agent;
		agent->type = type;
		agent->pos = pos;
		agent->starvationTime = 0;

		assert(mLattice[index(pos)] == 0);
		mLattice[index(pos)] = agent;

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

		mLattice[index(agent->pos)] = 0;
		delete agent;
	}

	~Model() {
		std::vector<Agent*>::iterator ai = mLattice.begin();;
		std::vector<Agent*>::iterator aend = mLattice.end();

		for (; ai != aend; ai++) {
			delete *ai;
		}
	}

	void initialize() {
		assert(mParams.initialPredatorCount + mParams.initialPreyCount < mSizeI);

		std::vector<Eigen::Vector2i> positions;
		for (int x = 0; x < mSizeX; x++) {
			for (int y = 0; y < mSizeY; y++) {
				positions.push_back(Eigen::Vector2i(x, y));
			}
		}

		std::random_shuffle(positions.begin(), positions.end());

		std::vector<Eigen::Vector2i>::iterator start;
		std::vector<Eigen::Vector2i>::iterator end;

		start = positions.begin();
		end = positions.begin() + mParams.initialPredatorCount;

		std::for_each(
			start, end,
			std::bind(&Model::create, this, std::placeholders::_1, Agent::PREDATOR)
		);

		start = end;
		end = start + mParams.initialPreyCount;

		std::for_each(
			start, end,
			std::bind(&Model::create, this, std::placeholders::_1, Agent::PREY)
		);
	}

	void neighbors(std::vector<Eigen::Vector2i>& positions, const Eigen::Vector2i& pos) {
		positions.clear();
		
		static Eigen::Vector2i r1 = Eigen::Vector2i(1, 0);
		static Eigen::Vector2i r2 = Eigen::Vector2i(-1, 0);
		static Eigen::Vector2i r3 = Eigen::Vector2i(0, 1);
		static Eigen::Vector2i r4 = Eigen::Vector2i(0, -1);

		if (pos[0] + 1 < mSizeX)
			positions.push_back(pos + r1);

		if (pos[0] - 1 >= 0)
			positions.push_back(pos + r2);
		
		if (pos[1] + 1 < mSizeY)
			positions.push_back(pos + r3);
		
		if (pos[1] -1 >= 0)
			positions.push_back(pos + r4);
	}

	bool is_not_within(const Eigen::Vector2i& pos, int area) {
		return mTerrain(pos[0], pos[1]) != area;
	}

	bool is_prey(const Eigen::Vector2i& pos) {
		return mPreys(pos[0], pos[1]) > 0;
	}

	bool is_predator(const Eigen::Vector2i& pos) {
		return mPredators(pos[0], pos[1]) > 0;
	}

	bool is_not_free(const Eigen::Vector2i& pos) {
		return is_prey(pos) || is_predator(pos);
	}

	void step_agent(Agent* agent) {
		agent->starvationTime += 1;

		if (agent->starvationTime > mParams.starvationTime) {
			return remove(agent);
		}

		bool migration = frand() < mParams.migrationRate;

		std::vector<Eigen::Vector2i> positions;
		std::vector<Eigen::Vector2i>::iterator pi;
		std::vector<Eigen::Vector2i>::iterator pend;

		if (frand() < mParams.movementRate) {
			neighbors(positions, agent->pos);
			pi = positions.begin();
			pend = positions.end();

			pend = std::remove_if(pi, pend, std::bind(&Model::is_not_free, this, std::placeholders::_1));

			// TODO: Starvation time regulation for crossings for prey?!
			if (/*agent->type == Agent::PREY ||*/ !migration) {
				pend = std::remove_if(pi, pend, std::bind(&Model::is_not_within, this, std::placeholders::_1, mTerrain(agent->pos[0], agent->pos[1])));
			}

			if (pi != pend) {
				std::random_shuffle(pi, pend);
				move(agent, *(positions.begin()));
			}
		}

		neighbors(positions, agent->pos);
		pi = positions.begin();
		pend = positions.end();

		if (!migration) {
			pend = std::remove_if(pi, pend, std::bind(&Model::is_not_within, this, std::placeholders::_1, mTerrain(agent->pos[0], agent->pos[1])));
		}

		//bool safe = pend == positions.end();

		if (agent->type == Agent::PREY) {
			pend = std::remove_if(pi, pend, std::bind(&Model::is_not_free, this, std::placeholders::_1));
		
			// TODO: How to involve starvation time for prey?
			// Python model line 170
			agent->starvationTime = 0;

			if (frand() < mParams.preyBirthRate && pi != pend) {
				std::random_shuffle(pi, pend);
				create(*(positions.begin()), Agent::PREY);
			}
		} else if (agent->type == Agent::PREDATOR) {
			for (; pi != pend; pi++) {
				if (is_prey(*pi)) {
					agent->starvationTime = 0;
					remove(mLattice[index(*pi)]);

					if (frand() < mParams.predatorBirthRate) {
						create(*pi, Agent::PREDATOR);
					}
				}
			}
		}
	}

	void step() {
		std::random_shuffle(mIndices.begin(), mIndices.end());

		std::vector<int>::iterator it = mIndices.begin();
		std::vector<int>::iterator iend = mIndices.end();

		for (; it != iend; it++) {
			if (mLattice[*it]) step_agent(mLattice[*it]);
		}
	}
};

struct ModelRenderer {
	GLFWwindow* mWindow;
	bool mRunning = true;
	Model& mModel;
	int mSteps = 0;

	ModelRenderer(Model& model) : mModel(model) {
		glfwInit();
		mWindow = glfwCreateWindow(600, 600, "SOCS", NULL, NULL);

		if (mWindow) {
			glfwMakeContextCurrent(mWindow);
		}
	}

	void step() {
		mSteps += 1;
		if (glfwWindowShouldClose(mWindow)) mRunning = false;

		std::ostringstream title;
		title << "Iteration " << mSteps;

		glfwSetWindowTitle(mWindow, title.str().c_str());

		if (mRunning) {
			float ratio;
	        int width, height;

	        glfwGetFramebufferSize(mWindow, &width, &height);
	        ratio = width / (float) height;

	        glViewport(0, 0, width, height);
	        glClear(GL_COLOR_BUFFER_BIT);
	        glMatrixMode(GL_PROJECTION);
	        glLoadIdentity();

	        //glOrtho(-ratio, ratio, 0.0, (float)mModel.mTerrain.rows(), 0.0, (float)mModel.mTerrain.cols());
	        gluOrtho2D(0.0, (float)mModel.mTerrain.rows(), 0.0, (float)mModel.mTerrain.cols());
	        glPointSize(5.0);

	        glMatrixMode(GL_MODELVIEW);
	        glLoadIdentity();

	        float color = 0.0;
	        float maxc = mModel.mTerrain.maxCoeff();

	        glBegin(GL_QUADS);
	        for (int x = 0; x < mModel.mSizeX; x++) {
	        	for (int y = 0; y < mModel.mSizeY; y++) {
	        		color = 0.5 * mModel.mTerrain(x, y) / maxc;
	        		glColor3f(color, color, color);
	        		glVertex2f(x, y);
	        		glVertex2f(x + 1, y);
	        		glVertex2f(x + 1, y + 1);
	        		glVertex2f(x, y + 1);
	        	}
	        }
	        glEnd();

	        glBegin(GL_POINTS);

        	auto ai = mModel.mLattice.begin();
        	auto aend = mModel.mLattice.end();

        	for (; ai != aend; ai++) {
        		Agent* agent = *ai;

        		if (agent) {
	        		if (agent->type == Agent::PREDATOR) {
	        			glColor3f(1.0, 0.0, 0.0);
	        			glVertex2f(agent->pos[0] + 0.0, agent->pos[1] + 0.1);
	        		}

	        		if (agent->type == Agent::PREY) {
	        			glColor3f(0.0, 0.0, 1.0);
	        			glVertex2f(agent->pos[0], agent->pos[1]);
	        		}
	        	}
        	}

	        glEnd();

	        glfwSwapBuffers(mWindow);
		}

		glfwPollEvents();
	}

	~ModelRenderer() {
		if (mWindow) glfwDestroyWindow(mWindow);
		glfwTerminate();
	}
};

Params create_params() {
	Params params;
	int s = 32;

	params.migrationRate = 0.01;
	params.starvationTime = 50;
	params.movementRate = 0.8;

	params.preyBirthRate = 0.06;
	params.predatorBirthRate = 0.5; //0.1;

	params.initialPreyCount = s * 6; //200;
	params.initialPredatorCount = 120;//s / 3;

	Eigen::MatrixXi area1 = Eigen::MatrixXi::Constant(s, s, 1);
	Eigen::MatrixXi area2 = Eigen::MatrixXi::Constant(s, s, 2);
	Eigen::MatrixXi area3 = Eigen::MatrixXi::Constant(s, s, 3);
	Eigen::MatrixXi area4 = Eigen::MatrixXi::Constant(s, s, 4);
	Eigen::MatrixXi area5 = Eigen::MatrixXi::Constant(s, s, 5);
	Eigen::MatrixXi area6 = Eigen::MatrixXi::Constant(s, s, 6);
	Eigen::MatrixXi area7 = Eigen::MatrixXi::Constant(s, s, 7);
	Eigen::MatrixXi area8 = Eigen::MatrixXi::Constant(s, s, 8);
	Eigen::MatrixXi area9 = Eigen::MatrixXi::Constant(s, s, 9);

	Eigen::MatrixXi row1(s, 3 * s);
	row1 << area1, area2, area3;

	Eigen::MatrixXi row2(s, 3 * s);
	row2 << area4, area5, area6;

	Eigen::MatrixXi row3(s, 3 * s);
	row3 << area7, area8, area9;

	Eigen::MatrixXi terrain(3 * s, 3 * s);
	terrain << row1, row2, row3;
	//terrain << area1, area2, area3, area4, area5, area6, area7, area8;

	params.terrain = terrain;
	return params;
}

int simulation(int argc, char* argv[]) {
	srand(time(0));
	Params params = create_params();

	Model model(params);
	ModelRenderer renderer(model);

	std::ofstream stream("pp.txt");

	while (renderer.mRunning) {
		model.step();
		renderer.step();

		stream << model.mPreys.sum() << " " << model.mPredators.sum() << std::endl;
	}

	return 1;
}

void worker(Params params, float& totalTime, boost::mutex& mtx) {
	const float maximumTime = 5000;

	Model model(params);
	float processTime = 0.0;

	while (processTime < maximumTime) {
		if (model.mPredators.sum() == 0) break;
		processTime += 1.0;
		model.step();
	}

	boost::mutex::scoped_lock lock(mtx);
	//std::cout << processTime << std::endl;
	totalTime += processTime;
}

int validation(int argc, char* argv[]) {
	const int K = 100;
	const int T = 5000;

	srand(time(0));

	Params params;

	params.migrationRate = 1.0;
	params.starvationTime = 50;
	params.movementRate = 0.8;

	params.preyBirthRate = 0.06;
	params.predatorBirthRate = 0.01;

	params.initialPreyCount = 0.25 * (256 * 4);
	params.initialPredatorCount = 0.1 * (256 * 4);

	Eigen::MatrixXi row1(16, 2 * 16);
	row1 << Eigen::MatrixXi::Constant(16, 16, 1), Eigen::MatrixXi::Constant(16, 16, 2);

	Eigen::MatrixXi row2(16, 2 * 16);
	row2 << Eigen::MatrixXi::Constant(16, 16, 3), Eigen::MatrixXi::Constant(16, 16, 4);

	Eigen::MatrixXi terrain(2 * 16, 2 * 16);
	terrain << row1, row2;

	params.terrain = terrain;

	Eigen::ArrayXf alive(5000);

	for (int k = 0; k < K; k++) {
		Model model(params);

		for (int t = 0; t < T; t++) {
			if (model.mPredators.sum() > 0) {
				alive[t] += 1.0;
			} else {
				break;
			}

			model.step();
		}

		std::cout << k << std::endl;
	}

	std::ofstream stream("alive32x32.txt");
	stream << alive;

	return 1;
}

int measurement(int argc, char* argv[]) {
	const int K = 10;

	Eigen::ArrayXf initialFractions = Eigen::ArrayXf::LinSpaced(11, 0.00, 0.5);
	Eigen::ArrayXf migrationRates = Eigen::ArrayXf::LinSpaced(11, 0.0, 1.0);

	srand(time(0));
	Params params = create_params();

	boost::threadpool::pool pool(8);
	boost::mutex mtx;

	for (int i = 0; i < migrationRates.rows(); i++) {
		params.migrationRate = migrationRates[i];

		for (int j = 0; j < initialFractions.rows(); j++) {
			float f = initialFractions[j];
			params.initialPredatorCount = (int)((f / (1.0 - f)) * params.initialPreyCount);

			float totalTime = 0.0;

			for (int k = 0; k < K; k++) {
				pool.schedule(std::bind(&worker, params, boost::ref(totalTime), boost::ref(mtx)));
			}

			pool.wait();
			float averageTime = totalTime / (float)K;

			std::cout << params.migrationRate << " ";
			std::cout << f << " ";
			std::cout << averageTime << std::endl;
		}
	}

	return 1;
}

int main(int argc, char* argv[]) {
	//return validation(argc, argv);
	//return measurement(argc, argv);
	return simulation(argc, argv);
}
