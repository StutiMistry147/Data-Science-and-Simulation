bool locked = false; 
byte count = 0;     

active [2] proctype SimulationThread() {
    do
    ::
        atomic {
            !locked -> locked = true;
        }
        count++;
        printf("Thread %d entered critical section. Active: %d\n", _pid, count);
        assert(count <= 1);
        count--;
        locked = false;
        
        printf("Thread %d exited critical section.\n", _pid);
    od
}
