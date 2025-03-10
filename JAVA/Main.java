import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

public class Main {
    private static final Scanner scanner = new Scanner(System.in);
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd-MM-yyyy");

    public static void main(String[] args) {
        TaskLinkedList taskList = new TaskLinkedList();
        while (true) {
            System.out.println("\nTASK MANAGER MENU");
            System.out.println("1. Add Task");
            System.out.println("2. Complete Task");
            System.out.println("3. Display Tasks");
            System.out.println("4. Reverse Display");
            System.out.println("5. Count Tasks");
            System.out.println("6. Clear Tasks");
            System.out.println("7. Exit");
            System.out.print("Enter choice: ");
            int choice = scanner.nextInt();
            scanner.nextLine();

            switch (choice) {
                case 1:
                    System.out.print("Enter task description: ");
                    String description = scanner.nextLine();
                    System.out.print("Enter task priority: ");
                    int priority = scanner.nextInt();
                    scanner.nextLine();
                    System.out.print("Enter category: ");
                    String category = scanner.nextLine();
                    System.out.print("Enter due date (dd-MM-yyyy): ");
                    LocalDate dueDate = LocalDate.parse(scanner.nextLine(), formatter);
                    System.out.print("Enter recurrence: ");
                    String recurrence = scanner.nextLine();
                    Task newTask = new Task(description, priority, category, dueDate, recurrence);
                    taskList.addTask(newTask);
                    break;
                case 2:
                    System.out.print("Enter the task to complete: ");
                    String desc;
                    desc = scanner.nextLine();
                    boolean removed = taskList.removeTask(desc);
                    System.out.println(removed ? "Task '" + desc + "' completed and removed." : "Task not found!");
                    break;
                case 3:
                    taskList.displayTasks();
                    break;
                case 4:
                    taskList.reverseDisplay();
                    break;
                case 5:
                    System.out.println("Total pending tasks: " + taskList.countTasks());
                    break;
                case 6:
                    taskList.clearTasks();
                    System.out.println("All tasks have been cleared!");
                    break;
                case 7:
                    System.out.println("Goodbye!");
                    return;
                default:
                    System.out.println("Invalid choice! Try again.");
            }
        }
    }
}
