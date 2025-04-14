#ifndef TASKCHAIN_HPP
#define TASKCHAIN_HPP

#include "jobs.hpp"

namespace NP{
    template<class Time> struct TCD{
        std::vector<Time> EST_prev, DA_max, RT_max;
        std::vector<std::vector<Time>> z_min,z_max;
        std::vector<std::vector<size_t>> input_job_index;
    };

    template<class Time>
    struct Task_chain_result {
        std::vector<std::vector<Time>> data_ages;
        std::vector<std::vector<Time>> reaction_times;
    };

    template<class Time> class Task {
        public:
            static Task<Time> noTask(){return Task<Time>(-1);} // used for mapping EST_prev
        private:
            const unsigned long id;
        
        public:
            Task(const unsigned long id)
            : id(id)
            {
                //
            }
            bool operator<(const Task& other) const { return id < other.id; }
            bool operator==(const Task& other) const { return id == other.id; }
            bool operator==(const unsigned long other) const { return id == other; }
            const unsigned long get_id() const {
                return id;
            }
    };

    template<class Time> class Buffer {
        private:
            unsigned long id;
            std::string type;
            
        public:
            Buffer(unsigned long id, std::string type)
            : id(id), type(type)
            {
                //
            }
    };

    template<class Time>
    class Task_chain {
        public:
            //typedef std::vector<Task_chain<Time>> Task_chain_set;
            
        private:
        std::vector<Task<Time>> tasks;
        std::vector<std::string> buffers;
        std::string inputtype;
        const unsigned long id;
        public:
            Task_chain(
                std::vector<Task<Time>> tasks,
                std::vector<std::string> buffers,
                std::string inputtype,
                unsigned long id)
                : tasks(tasks), buffers(buffers), inputtype(inputtype), id(id)
            {
                //
            }
            std::vector<Task<Time>> get_tasks(){
                return tasks;
            }
            std::vector<std::string> get_buffers(){
                return buffers;
            }
            std::string get_inputtype(){
                return inputtype;
            }
            const unsigned long get_id() const {
                return id;
            }
            
            size_t get_task_index(std::vector<Task<Time>>& tasks, typename std::vector<Task<Time>>::iterator& task_iter) const{
                
                return std::distance(std::begin(tasks), task_iter);
            }


            bool operator<(const Task_chain<Time>& other) const { return id < other.id; }


    };
}
#endif