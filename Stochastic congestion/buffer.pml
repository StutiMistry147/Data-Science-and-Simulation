#define BUF_SIZE 5

byte buffer_count = 0;

active proctype Producer() {
    do
    ::  if
        :: buffer_count < BUF_SIZE -> 
            buffer_count++; 
            printf("Packet In: %d\n", buffer_count);
        :: else -> 
            printf("Buffer Full - Packet Dropped\n");
        fi;
    od
}

active proctype Consumer() {
    do
    ::  if
        :: buffer_count > 0 -> 
            buffer_count--; 
            printf("Packet Out: %d\n", buffer_count);
        :: else -> 
            skip;
        fi;
    od
}

/* Run: spin buffer.pml */
