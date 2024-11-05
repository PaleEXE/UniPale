#include <iostream>
#include <random>
#include <vector>
#include <numeric>
#include <algorithm>
#include <fstream>
#include <iomanip>

std::mt19937 gen(7124);
std::uniform_int_distribution<int> distribution_service_time(1, 3);
std::uniform_int_distribution<int> distribution_arrival_time(1, 5);
const int AMOUNT_OF_CARS = 20;

class Car {
public:
    static int last_time;
    int rand_arrival_number;
    int arrival_time;
    int service_time;

    Car(int arrival_time, int service_time) {
        this->rand_arrival_number = arrival_time;
        this->arrival_time = last_time + arrival_time;
        this->service_time = service_time;
        last_time = this->arrival_time;
    }

    static std::vector<Car> create_cars(int amount) {
        std::vector<Car> cars;
        cars.reserve(amount);
        cars.emplace_back(0, distribution_service_time(gen));
        for (int i = 1; i < amount; i++) {
            cars.emplace_back(distribution_arrival_time(gen), distribution_service_time(gen));
        }
        return cars;
    }
};

class TollBooth {
    std::vector<Car> cars;
    std::vector<std::vector<int>> times;
public:
    TollBooth(int amount_of_cars) : cars(Car::create_cars(amount_of_cars)) {
        times = this->calc_times();
    }

    std::vector<std::vector<int>> calc_times() {
        std::vector<std::vector<int>> metrics;
        std::vector<int> start_service_times, end_service_times, waiting_times, system_times, idle_times;

        int current_end_time = cars[0].arrival_time + cars[0].service_time;
        start_service_times.push_back(cars[0].arrival_time);
        end_service_times.push_back(current_end_time);
        waiting_times.push_back(0);
        system_times.push_back(cars[0].service_time);
        idle_times.push_back(cars[0].arrival_time);

        for (size_t i = 1; i < cars.size(); i++) {
            int start_time = std::max(cars[i].arrival_time, current_end_time);
            start_service_times.push_back(start_time);

            int system_time = start_time - cars[i].arrival_time + cars[i].service_time;
            system_times.push_back(system_time);

            int wait_time = start_time - cars[i].arrival_time;
            waiting_times.push_back(wait_time);

            current_end_time = start_time + cars[i].service_time;
            end_service_times.push_back(current_end_time);

            int idle_time = std::max(0, start_time - end_service_times[i - 1]);
            idle_times.push_back(idle_time);
        }

        metrics.push_back(start_service_times);
        metrics.push_back(end_service_times);
        metrics.push_back(waiting_times);
        metrics.push_back(system_times);
        metrics.push_back(idle_times);
        return metrics;
    }

    void display() {

        std::vector<std::string> headers = { "Index", "Arrival RN", "Service Time", "Arrival Time",
                                            "Start Time", "End Time", "Waiting Time", "System Time", "Idle Time" };
        int col_width = 12;

        for (const auto& header : headers) {
            std::cout << std::setw(col_width) << header << " | ";
        }
        std::cout << "\n" << std::string(headers.size() * (col_width + 3), '-') << "\n";

        for (size_t i = 0; i < cars.size(); i++) {
            std::cout << std::setw(col_width) << i << " | "
                << std::setw(col_width) << cars[i].rand_arrival_number << " | "
                << std::setw(col_width) << cars[i].service_time << " | "
                << std::setw(col_width) << cars[i].arrival_time << " | "
                << std::setw(col_width) << this->times[0][i] << " | "
                << std::setw(col_width) << this->times[1][i] << " | "
                << std::setw(col_width) << this->times[2][i] << " | "
                << std::setw(col_width) << this->times[3][i] << " | "
                << std::setw(col_width) << this->times[4][i] << "\n";
        }
        std::cout << "\n" << std::string(headers.size() * (col_width + 3), '-') << "\n";
    }

    void save_to_csv(const std::string& filename) {
        std::ofstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return;
        }

        file << "index,Arrival RN,Service,Arrival,Start,End,Waiting,System,Idle\n";
        for (size_t i = 0; i < cars.size(); i++) {
            file << i << ","
                << cars[i].rand_arrival_number << ","
                << cars[i].service_time << ","
                << cars[i].arrival_time << ","
                << this->times[0][i] << ","
                << this->times[1][i] << ","
                << this->times[2][i] << ","
                << this->times[3][i] << ","
                << this->times[4][i] << "\n";
        }

        int total_wait_time = std::accumulate(this->times[2].begin(), this->times[2].end(), 0);
        int total_system_time = std::accumulate(this->times[3].begin(), this->times[3].end(), 0);
        int total_idle_time = std::accumulate(this->times[4].begin(), this->times[4].end(), 0);

        file << "Total,,,," << "," << "," << total_wait_time << "," << total_system_time << "," << total_idle_time << "\n";
        file.close();
        std::cout << "Data saved to " << filename << std::endl;
    }
};

int Car::last_time = 0;

int main() {
    std::cout << "Mohammad Fadi Al-Hennawi (Pale_exe)" << std::endl;

    TollBooth booth(AMOUNT_OF_CARS);
    booth.display();
    booth.save_to_csv("cars_simulation.csv");

    std::cout << "Press Enter to continue...";
    std::cin.get();
    return 0;
}
