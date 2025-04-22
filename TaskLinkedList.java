import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

public class TaskLinkedList {
    private Task head;
    private Task tail;

    public Task getHead() {
        return head;
    }

    public void sortByPriority() {
        if (head == null || head.next == null) return;
        boolean swapped;
        do {
            swapped = false;
            Task current = head;
            while (current.next != null) {
                if (current.priority > current.next.priority) {
                    swapNodes(current, current.next);
                    swapped = true;
                } else {
                    current = current.next;
                }
            }
        } while (swapped);
    }

    public void sortByDate() {
        if (head == null || head.next == null) return;
        boolean swapped;
        do {
            swapped = false;
            Task current = head;
            while (current.next != null) {
                if (current.dueDate.isAfter(current.next.dueDate)) {
                    swapNodes(current, current.next);
                    swapped = true;
                } else {
                    current = current.next;
                }
            }
        } while (swapped);
    }

    private void swapNodes(Task a, Task b) {
        if (a == b) return;

        String tempDesc = a.description;
        a.description = b.description;
        b.description = tempDesc;

        int tempPriority = a.priority;
        a.priority = b.priority;
        b.priority = tempPriority;

        String tempCat = a.category;
        a.category = b.category;
        b.category = tempCat;

        LocalDate tempDate = a.dueDate;
        a.dueDate = b.dueDate;
        b.dueDate = tempDate;

        String tempRec = a.recurrence;
        a.recurrence = b.recurrence;
        b.recurrence = tempRec;
    }

    public String[] filterByCategory(String category) {
        List<String> filteredTasks = new ArrayList<>();
        Task current = head;
        while (current != null) {
            if (current.category.equalsIgnoreCase(category)) {
                filteredTasks.add(current.toString());
            }
            current = current.next;
        }
        return filteredTasks.toArray(new String[0]);
    }

    public String[] searchByKeyword(String keyword) {
        List<String> results = new ArrayList<>();
        Task current = head;
        while (current != null) {
            if (current.description.toLowerCase().contains(keyword.toLowerCase())) {
                results.add(current.toString());
            }
            current = current.next;
        }
        return results.toArray(new String[0]);
    }

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

    public boolean updateTask(String oldDescription, Task updatedTask) {
        Task current = head;
        while (current != null) {
            if (current.description.equalsIgnoreCase(oldDescription)) {
                current.description = updatedTask.description;
                current.priority = updatedTask.priority;
                current.category = updatedTask.category;
                current.dueDate = updatedTask.dueDate;
                current.recurrence = updatedTask.recurrence;
                sortByPriority();
                return true;
            }
            current = current.next;
        }
        return false;
    }

    public String[] getAllTasksAsArray() {
        List<String> tasks = new ArrayList<>();
        Task current = head;
        while (current != null) {
            tasks.add(current.toString());
            current = current.next;
        }
        return tasks.toArray(new String[0]);
    }

    public String[] getReversedTasksAsArray() {
        List<String> tasks = new ArrayList<>();
        Task current = tail;
        while (current != null) {
            tasks.add(current.toString());
            current = current.prev;
        }
        return tasks.toArray(new String[0]);
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