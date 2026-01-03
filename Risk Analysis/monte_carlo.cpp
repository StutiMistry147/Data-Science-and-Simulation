#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <thread>
#include <mutex>

std::mutex mtx;
std::ofstream results("sim_outcomes.csv");

void simulate_paths(int num_sims, double S0, double mu, double sigma, double T) {
    std::default_random_engine gen;
    std::normal_distribution<double> dist(0.0, 1.0);

    for (int i = 0; i < num_sims; ++i) {
        // Geometric Brownian Motion Formula
        double drift = (mu - 0.5 * sigma * sigma) * T;
        double diffusion = sigma * sqrt(T) * dist(gen);
        double final_price = S0 * exp(drift + diffusion);

        // Lock thread to write to shared file safely
        std::lock_guard<std::mutex> lock(mtx);
        results << final_price << "\n";
    }
}

int main() {
    results << "final_price\n";
    int total_sims = 100000;
    int threads = 4;
    
    std::vector<std::thread> worker_threads;
    for (int i = 0; i < threads; ++i) {
        worker_threads.push_back(std::thread(simulate_paths, total_sims/threads, 100.0, 0.05, 0.2, 1.0));
    }

    for (auto& t : worker_threads) t.join();
    std::cout << "Simulation Complete. 100,000 paths generated." << std::endl;
    return 0;
}
