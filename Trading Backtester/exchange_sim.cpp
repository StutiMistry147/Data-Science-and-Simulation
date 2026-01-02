#include <iostream>
#include <fstream>
#include <random>
#include <chrono>
#include <thread>

int main() {
    double price = 100.0;
    std::default_random_engine gen;
    // Normal distribution for small price shocks
    std::normal_distribution<double> noise(0, 0.05); 

    std::ofstream feed("market_data.csv");
    feed << "timestamp,ticker,price\n";

    std::cout << "Market Feed Started... Generating ticks to market_data.csv" << std::endl;

    while(true) {
        price += noise(gen); // Stochastic Random Walk
        auto ts = std::chrono::system_clock::now().time_since_epoch().count();
        
        feed << ts << ",AAPL," << price << std::endl;
        feed.flush(); // Ensure data is written immediately for the Python reader
        
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return 0;
}
