import java.time.LocalDate;
public class Task {
    String description;
    int priority;
    String category;
    LocalDate dueDate;
    String recurrence;
    Task next, prev; // Pointers for doubly linked list

    public Task(String description, int priority, String category, LocalDate dueDate, String recurrence) {
        this.description = description;
        this.priority = priority;
        this.category = category;
        this.dueDate = dueDate;
        this.recurrence = recurrence;
        this.next = null;
        this.prev = null;
    }

    @Override
    public String toString() {
        return "- " + description + " (Priority: " + priority + ", Category: " + category +
                ", Due: " + dueDate + ", Recurrence: " + recurrence + ")";
    }
}
