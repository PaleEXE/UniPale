#include <iostream>     // For input and output
#include <random>      // For generating random numbers
#include <vector>      // For using vectors (dynamic arrays)
#include <numeric>     // For numeric operations like accumulate
#include <algorithm>   // For algorithmic functions (like max)
#include <fstream>     // For file handling

// Initialize random number generator with a fixed seed for reproducibility
std::mt19937 gen(7124);
// Define uniform distributions for service time and arrival time
std::uniform_int_distribution<int> distribution_service_time(1, 3);
std::uniform_int_distribution<int> distribution_arrival_time(1, 5);
const int AMOUNT_OF_CARS = 20; // Constant for the number of cars to simulate

class Car {
public:
    static int last_time; // Static variable to keep track of the last time a car was created
    int rand_arraivel_number; // Random number betwwen each car
    int arrival_time;      // Arrival time of the car
    int service_time;      // Service time of the car

    // Constructor that initializes arrival and service times
    Car(int arrival_time, int service_time) {
        this->rand_arraivel_number = arrival_time;
        this->arrival_time = last_time + arrival_time; // Set arrival time based on last_time
        this->service_time = service_time;              // Set service time
        last_time = this->arrival_time;                 // Update last_time for the next car
    }

    // Function to create a specified number of cars with random times
    static std::vector<Car> create_cars(int amount) {
        std::vector<Car> cars; // Vector to hold created cars
        cars.reserve(amount);   // Reserve space for efficiency
        cars.emplace_back(0, distribution_service_time(gen)); // Create the first car with arrival time 0

        // Create subsequent cars with random arrival and service times
        for (int i = 1; i < amount; i++) {
            cars.emplace_back(
                distribution_arrival_time(gen),
                distribution_service_time(gen)
            );
        }
        return cars; // Return the vector of created cars
    }

    // Function to calculate various time metrics for each car
    static std::vector<std::vector<int>> calc_times(const std::vector<Car>* cars_ptr) {
        const auto& cars = *cars_ptr; // Dereference pointer to access cars
        std::vector<std::vector<int>> rizz; // Vector to store different time metrics
        std::vector<int> start_service_times; // Vector for start times of service
        std::vector<int> end_service_times;   // Vector for end times of service
        std::vector<int> waiting_times;        // Vector for waiting times
        std::vector<int> system_times;        // Vector for car in system times
        std::vector<int> idle_times;           // Vector for idle times

        // Initialize the first car's timings
        int current_end_time = cars[0].arrival_time + cars[0].service_time;
        start_service_times.push_back(cars[0].arrival_time);
        end_service_times.push_back(current_end_time);
        waiting_times.push_back(0);
        system_times.push_back(cars[0].service_time);
        idle_times.push_back(cars[0].arrival_time);

        // Loop through the cars starting from the second one
        for (size_t i = 1; i < cars.size(); i++) {
            // Calculate start time as the later of arrival time and current end time
            int start_time = std::max(cars[i].arrival_time, current_end_time);
            start_service_times.push_back(start_time);

            // Calculate system time
            int system_time = start_time - cars[i].arrival_time + cars[i].service_time;
            system_times.push_back(system_time);

            // Calculate wait time
            int waite_time = start_time - cars[i].arrival_time;
            waiting_times.push_back(waite_time);

            // Update current end time
            current_end_time = start_time + cars[i].service_time;
            end_service_times.push_back(current_end_time);

            // Calculate idle time based on the difference between current start time and previous end time
            int idle_time = std::max(0, start_time - end_service_times[i - 1]);
            idle_times.push_back(idle_time);
        }

        // Store all calculated times in the rizz vector
        rizz.push_back(start_service_times);
        rizz.push_back(end_service_times);
        rizz.push_back(waiting_times);
        rizz.push_back(system_times);
        rizz.push_back(idle_times);
        return rizz; // Return the vector containing all time metrics
    }

    // Function to save car data and timings to a CSV file
    static void save_to_csv(const std::vector<Car>& cars, const std::vector<std::vector<int>>& times, const std::string& filename) {
        std::ofstream file(filename); // Open the specified file
        if (!file.is_open()) { // Check if the file opened successfully
            std::cerr << "Error opening file: " << filename << std::endl;
            return;
        }

        // Write the header for the CSV file
        file << "index,Arrival RN,Service,Arrival,Start,End,Waiting,System,Idle\n";

        // Write each car's information into the CSV
        for (size_t i = 0; i < cars.size(); i++) {
            file << i << ","
                << cars[i].rand_arraivel_number << ","
                << cars[i].service_time << ","
                << cars[i].arrival_time << ","
                << times[0][i] << ","
                << times[1][i] << ","
                << times[2][i] << ","
                << times[3][i] << ","
                << times[4][i] << "\n";
        }

        // Calculate total waiting and idle times
        int total_wait_time = std::accumulate(times[2].begin(), times[2].end(), 0);
        int total_system_time = std::accumulate(times[3].begin(), times[3].end(), 0);
        int total_idle_time = std::accumulate(times[4].begin(), times[4].end(), 0);

        // Write the totals to the CSV file
        file << "Total," << "," << "," << "," << "," << "," << total_wait_time << "," << total_system_time << "," << total_idle_time << "\n";

        file.close(); // Close the file
        std::cout << "Data saved to " << filename << std::endl; // Notify the user that data was saved
    }
};

// Initialize static member variable
int Car::last_time = 0;

int main() {
    std::cout << "Mohammad Fadi Al-Hennawi (Pale_exe)" << std::endl;
    // Create a vector of cars
    std::vector<Car> cars = Car::create_cars(AMOUNT_OF_CARS);
    // Calculate times related to each car
    std::vector<std::vector<int>> rizz = Car::calc_times(&cars);
    std::vector<int> start_list = rizz[0];
    std::vector<int> end_list = rizz[1];
    std::vector<int> waiting_list = rizz[2];
    std::vector<int> system_list = rizz[3];
    std::vector<int> idle_list = rizz[4];

    // Output car details to the console
    for (size_t i = 0; i < cars.size(); i++) {
        std::cout << i << " - "
            << "Arrival RN: " << cars[i].rand_arraivel_number
            << ", Service Time: " << cars[i].service_time
            << ", Arrival Time: " << cars[i].arrival_time
            << ", Start Time: " << start_list[i]
            << ", End Time: " << end_list[i]
            << ", Waiting Time: " << waiting_list[i]
            << ", Sestem Time: " << system_list[i]
            << ", Idle Time: " << idle_list[i] << std::endl;
    }

    // Display the total waiting and idle times
    std::cout << "SUM(Waiting Times) = " << std::accumulate(waiting_list.begin(), waiting_list.end(), 0) << std::endl;
    std::cout << "SUM(Sestem Times) = " << std::accumulate(system_list.begin(), system_list.end(), 0) << std::endl;
    std::cout << "SUM(Idle Times) = " << std::accumulate(idle_list.begin(), idle_list.end(), 0) << std::endl;

    // Save car data and timings to a CSV file
    Car::save_to_csv(cars, rizz, "cars_simulation.csv");

    // Wait for the user to press Enter before exiting
    std::cout << "Press Enter to continue...";
    std::cin.get(); // Wait for the user to press Enter
    return 0; // Return success status
}
