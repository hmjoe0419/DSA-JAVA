public class TaskLinkedList {
    private Task head;
    private Task tail;

    public void addTask(Task newTask) {
        if (head == null) {
            head = tail = newTask;
        } else {
            tail.next = newTask;
            newTask.prev = tail;
            tail = newTask;
        }
        sortByPriority();
    }

    public boolean removeTask(String description) {
        Task current = head;
        while (current != null) {
            if (current.description.equalsIgnoreCase(description)) {
                if (current.prev != null) {
                    current.prev.next = current.next;
                } else {
                    head = current.next;
                }
                if (current.next != null) {
                    current.next.prev = current.prev;
                } else {
                    tail = current.prev;
                }
                return true;
            }
            current = current.next;
        }
        return false;
    }

    public void displayTasks() {
        if (head == null) {
            System.out.println("No pending tasks!");
            return;
        }
        Task current = head;
        while (current != null) {
            System.out.println(current);
            current = current.next;
        }
    }

    public void reverseDisplay() {
        if (tail == null) {
            System.out.println("No tasks to display!");
            return;
        }
        Task current = tail;
        while (current != null) {
            System.out.println(current);
            current = current.prev;
        }
    }

    public void sortByPriority() {
        if (head == null || head.next == null) return;
        boolean swapped;
        do {
            swapped = false;
            Task current = head;
            while (current.next != null) {
                if (current.priority > current.next.priority) {
                    int tempPriority = current.priority;
                    current.priority = current.next.priority;
                    current.next.priority = tempPriority;

                    String tempDesc = current.description;
                    current.description = current.next.description;
                    current.next.description = tempDesc;

                    swapped = true;
                }
                current = current.next;
            }
        } while (swapped);
    }

    public int countTasks() {
        int count = 0;
        Task current = head;
        while (current != null) {
            count++;
            current = current.next;
        }
        return count;
    }

    public void clearTasks() {
        head = tail = null;
    }
}
