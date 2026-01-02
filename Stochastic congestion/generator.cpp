#include <iostream>
#include <fstream>
#include <random>
#include <chrono>
#include <cmath>

int main() {
    // Parameters
    const double lambda = 10.0; // Average 10 packets per second
    const int total_packets = 100000; // Generate 100k data points
    
    std::ofstream file("network_traffic.csv");
    file << "timestamp,inter_arrival_time,packet_size\n";

    std::default_random_engine gen;
    // Inter-arrival times for Poisson process follow Exponential Distribution
    std::exponential_distribution<double> dist(lambda);
    std::uniform_int_distribution<int> size_dist(64, 1500); // Standard MTU sizes

    double current_time = 0.0;

    for (int i = 0; i < total_packets; ++i) {
        double interval = dist(gen);
        current_time += interval;
        int p_size = size_dist(gen);

        file << current_time << "," << interval << "," << p_size << "\n";
    }

    file.close();
    std::cout << "Successfully generated " << total_packets << " data points." << std::endl;
    return 0;
}
