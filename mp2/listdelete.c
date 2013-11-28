#include <stdio.h>
#include <stdlib.h>

#define ALIGNMENT 8 
#define SHIFT 3
#define align(size) ((((size-1)>>SHIFT)<<SHIFT)+ALIGNMENT)

#define NEXTPTR(node) ((boundary*)(node+1))
#define PREVPTR(node) ((boundary*)(((size_t*)(node+1)+1)))

#define pm(ptr) printf("%p\n",ptr);
#define pi(x) printf("%d\n",x);

typedef struct s_boundary{
	size_t size;
}*boundary;



boundary makeNode(int size){
	size  = align(size);
	boundary node = (boundary)malloc(size + sizeof(struct s_boundary));
	node->size= size;
	boundary* nextNode = NEXTPTR(node);
	boundary* prevNode = PREVPTR(node);
	*nextNode = *prevNode = NULL;
	printf("%d : %p\n", size,node);
	return node;
}

void addnode(boundary* head, boundary node){
	if(*head == NULL){
		*head = node;
		return;
	}

	boundary* nextnode = NEXTPTR(node);
	boundary* prevhead = PREVPTR(*head);
	*nextnode = *head;
	*prevhead = node;
	*head = node;
	return;
}

void deleteNode(boundary* head, boundary node){
	if(*head == NULL)	return;
    boundary *prev = PREVPTR(node);
    boundary *next = NEXTPTR(node);
    if((*prev) != NULL){
		boundary* prevnext = NEXTPTR(*prev);
		*prevnext= *next;
	}
	if(*next!=NULL){
		boundary* nextprev = PREVPTR(*next);
		*nextprev = *prev;
	}
	if(*prev==NULL){//now we need to move the head
		*head = *next; //this also handles the case when *next is NULL
	}
	return;
}

void traverse_list(boundary head){
	if(head==NULL){
		printf("%s\n", "Empty list, returning");
		return;
	}
	while(head!=NULL){
		printf("%lu\n", head->size);
		head = *NEXTPTR(head);
	}
	return;
}

int main(){

	boundary head = NULL;
	boundary x = makeNode(32);	addnode(&head, x);
	boundary x1 = makeNode(24);	addnode(&head, x1);
	boundary x2 = makeNode(16);	addnode(&head, x2);
	boundary x3 = makeNode(8);	addnode(&head, x3);
	deleteNode(&head, x);
	traverse_list(head);

}

