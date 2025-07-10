#ifndef TASKCHAIN_HPP
#define TASKCHAIN_HPP

#include "jobs.hpp"

namespace NP{
    template<class Time> struct TCD{
        std::vector<Time> DA_max, RT_max, EST_prev; // per task chain
        std::vector<std::vector<Time>> EIT_Reac_int, EIT_Age_int, LIT_int; // per task per task chain
        std::vector<std::vector<Time>> EIT_Reac_out, EIT_Age_out, LIT_out; // per task per task chain
    };

    template<class Time>
    struct Task_chain_result {
        std::vector<std::vector<Time>> data_ages;
        std::vector<std::vector<Time>> reaction_times;
    };

    template<class Time>
    class Task_chain {
        public:
            //typedef std::vector<Task_chain<Time>> Task_chain_set;
            
        private:
        const std::vector<unsigned long> tasks;
        const bool event_input;
        const bool active_output;
        const unsigned long id;
        public:
            Task_chain(
                const std::vector<unsigned long>& tasks,
                const bool& event_input,
                const bool& active_output,
                const unsigned long id)
                : tasks(tasks), event_input(event_input), active_output(active_output), id(id)
            {
                //
            }
            const std::vector<unsigned long>& get_tasks()const{
                return tasks;
            }
            const bool uses_event_input()const{
                return event_input;
            }
            const bool uses_active_output()const{
                return active_output;
            }
            const unsigned long get_id() const {
                return id;
            }
            
            size_t get_task_index(const std::vector<unsigned long>& tasks, const unsigned long& task_id) const{
                return std::distance(std::begin(tasks), std::find(std::begin(tasks), std::end(tasks), task_id));
            }


    };
}
#endif