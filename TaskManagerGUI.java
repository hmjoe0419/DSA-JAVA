import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class TaskManagerGUI extends JFrame {
    private TaskLinkedList taskList;
    private DefaultListModel<String> listModel;
    private JList<String> taskJList;
    private JTextField searchField;
    private boolean darkMode = false;
    private DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("dd-MM-yyyy");

    private JPanel mainPanel, listPanel, sidePanel, buttonPanel, headerPanel;
    private JButton toggleThemeBtn;

    public TaskManagerGUI() {
        taskList = new TaskLinkedList();
        initializeUI();
    }

    private void initializeUI() {
        setTitle("Task Manager");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1000, 600);
        setLocationRelativeTo(null);

        mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(new EmptyBorder(15, 15, 15, 15));
        add(mainPanel);

        // Header
        headerPanel = new JPanel(new BorderLayout());
        JLabel titleLabel = new JLabel("Task Manager", SwingConstants.CENTER);
        titleLabel.setFont(new Font("Arial", Font.BOLD, 28));
        headerPanel.add(titleLabel, BorderLayout.CENTER);

        // Theme Toggle Button
        toggleThemeBtn = new JButton("🌙 Dark Mode");
        toggleThemeBtn.setFont(new Font("Arial", Font.PLAIN, 14));
        toggleThemeBtn.addActionListener(e -> toggleTheme());
        headerPanel.add(toggleThemeBtn, BorderLayout.EAST);

        mainPanel.add(headerPanel, BorderLayout.NORTH);

        // Center Panel
        listPanel = new JPanel(new BorderLayout());
        listPanel.setBorder(BorderFactory.createTitledBorder("Tasks"));

        listModel = new DefaultListModel<>();
        taskJList = new JList<>(listModel);
        taskJList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        taskJList.setFont(new Font("Arial", Font.PLAIN, 14));
        JScrollPane scrollPane = new JScrollPane(taskJList);
        listPanel.add(scrollPane, BorderLayout.CENTER);
        mainPanel.add(listPanel, BorderLayout.CENTER);

        // Sort/Filter/Search Panel
        sidePanel = new JPanel();
        sidePanel.setLayout(new BoxLayout(sidePanel, BoxLayout.Y_AXIS));
        sidePanel.setBorder(BorderFactory.createTitledBorder("Sort / Filter / Search"));
        sidePanel.setPreferredSize(new Dimension(220, 300));

        JButton sortPriorityBtn = new JButton("Sort by Priority");
        JButton sortDateBtn = new JButton("Sort by Date");
        JButton filterCategoryBtn = new JButton("Filter by Category");

        Font buttonFont = new Font("Arial", Font.PLAIN, 14);
        for (JButton btn : new JButton[]{sortPriorityBtn, sortDateBtn, filterCategoryBtn}) {
            btn.setAlignmentX(Component.CENTER_ALIGNMENT);
            btn.setFont(buttonFont);
            btn.setMaximumSize(new Dimension(200, 35));
            btn.setFocusable(false);
            sidePanel.add(Box.createVerticalStrut(10));
            sidePanel.add(btn);
        }

        sortPriorityBtn.addActionListener(e -> {
            taskList.sortByPriority();
            updateTaskList();
        });

        sortDateBtn.addActionListener(e -> {
            taskList.sortByDate();
            updateTaskList();
        });

        filterCategoryBtn.addActionListener(e -> {
            String category = JOptionPane.showInputDialog(this, "Enter category to filter:");
            if (category != null && !category.trim().isEmpty()) {
                listModel.clear();
                for (String task : taskList.filterByCategory(category.trim())) {
                    listModel.addElement(task);
                }
            }
        });

        // Search Field + Button
        sidePanel.add(Box.createVerticalStrut(20));
        JLabel searchLabel = new JLabel("Search Keyword:");
        searchLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        sidePanel.add(searchLabel);

        searchField = new JTextField();
        searchField.setMaximumSize(new Dimension(200, 30));
        sidePanel.add(searchField);

        JButton searchBtn = new JButton("Search");
        searchBtn.setFont(buttonFont);
        searchBtn.setMaximumSize(new Dimension(200, 30));
        searchBtn.setAlignmentX(Component.CENTER_ALIGNMENT);
        searchBtn.addActionListener(e -> {
            String keyword = searchField.getText().trim();
            if (!keyword.isEmpty()) {
                listModel.clear();
                for (String task : taskList.searchByKeyword(keyword)) {
                    listModel.addElement(task);
                }
            }
        });

        sidePanel.add(Box.createVerticalStrut(10));
        sidePanel.add(searchBtn);

        mainPanel.add(sidePanel, BorderLayout.EAST);

        // Bottom Button Panel
        buttonPanel = new JPanel(new GridLayout(1, 7, 10, 10));
        String[] buttonLabels = {"Add Task", "Modify Task", "Complete Task", "Display Tasks",
                "Reverse Display", "Count Tasks", "Clear Tasks"};

        for (String label : buttonLabels) {
            JButton button = new JButton(label);
            button.setFont(new Font("Arial", Font.PLAIN, 14));
            button.addActionListener(new ButtonClickListener());
            buttonPanel.add(button);
        }

        mainPanel.add(buttonPanel, BorderLayout.SOUTH);
        updateTaskList();
        applyTheme(); // Initial theme application
    }

    private void toggleTheme() {
        darkMode = !darkMode;
        toggleThemeBtn.setText(darkMode ? "☀ Light Mode" : "🌙 Dark Mode");
        applyTheme();
    }

    // Entire code remains structurally the same up to applyTheme()
// Replace only the applyTheme() method with this improved one:

private void applyTheme() {
    Color bgColor = darkMode ? new Color(40, 40, 40) : Color.WHITE;
    Color fgColor = darkMode ? new Color(230, 230, 230) : Color.BLACK;
    Color btnBgColor = darkMode ? new Color(70, 70, 70) : new JButton().getBackground();
    Color btnFgColor = darkMode ? Color.WHITE : Color.BLACK;
    Color borderColor = darkMode ? Color.LIGHT_GRAY : Color.GRAY;
    Color textFieldBg = darkMode ? new Color(60, 60, 60) : Color.WHITE;
    Color textFieldFg = darkMode ? Color.WHITE : Color.BLACK;

    Component[] panels = {mainPanel, listPanel, sidePanel, buttonPanel, headerPanel};
    for (Component comp : panels) {
        comp.setBackground(bgColor);
        comp.setForeground(fgColor);
        if (comp instanceof JPanel) {
            for (Component child : ((JPanel) comp).getComponents()) {
                child.setBackground(bgColor);
                child.setForeground(fgColor);
                if (child instanceof JButton) {
                    child.setBackground(btnBgColor);
                    child.setForeground(btnFgColor);
                } else if (child instanceof JLabel) {
                    child.setForeground(fgColor);
                } else if (child instanceof JTextField) {
                    child.setBackground(textFieldBg);
                    child.setForeground(textFieldFg);
                    ((JTextField) child).setCaretColor(Color.CYAN);
                }
            }
        }
    }

    // Theme for list
    taskJList.setBackground(textFieldBg);
    taskJList.setForeground(textFieldFg);
    taskJList.setSelectionBackground(darkMode ? new Color(100, 100, 255) : new Color(173, 216, 230));
    taskJList.setSelectionForeground(Color.WHITE);
    taskJList.setBorder(BorderFactory.createLineBorder(borderColor));

    // Text field theme
    searchField.setBackground(textFieldBg);
    searchField.setForeground(textFieldFg);
    searchField.setCaretColor(Color.CYAN);

    // Toggle button styling
    toggleThemeBtn.setBackground(btnBgColor);
    toggleThemeBtn.setForeground(btnFgColor);

    // Set border/title color for titled borders
    listPanel.setBorder(BorderFactory.createTitledBorder(
            BorderFactory.createLineBorder(borderColor),
            "Tasks",
            0, 0,
            null,
            fgColor
    ));

    sidePanel.setBorder(BorderFactory.createTitledBorder(
            BorderFactory.createLineBorder(borderColor),
            "Sort / Filter / Search",
            0, 0,
            null,
            fgColor
    ));
}


    private void updateTaskList() {
        listModel.clear();
        for (String task : taskList.getAllTasksAsArray()) {
            listModel.addElement(task);
        }
    }

    private void updateReversedTaskList() {
        listModel.clear();
        for (String task : taskList.getReversedTasksAsArray()) {
            listModel.addElement(task);
        }
    }

    private void showAddTaskDialog() {
        JPanel panel = new JPanel(new GridLayout(5, 2, 5, 5));

        JTextField descriptionField = new JTextField();
        JSpinner prioritySpinner = new JSpinner(new SpinnerNumberModel(1, 1, 10, 1));
        JTextField categoryField = new JTextField();
        JTextField dueDateField = new JTextField();
        JTextField recurrenceField = new JTextField();

        panel.add(new JLabel("Description:"));
        panel.add(descriptionField);
        panel.add(new JLabel("Priority (1-10):"));
        panel.add(prioritySpinner);
        panel.add(new JLabel("Category:"));
        panel.add(categoryField);
        panel.add(new JLabel("Due Date (dd-MM-yyyy):"));
        panel.add(dueDateField);
        panel.add(new JLabel("Recurrence:"));
        panel.add(recurrenceField);

        int result = JOptionPane.showConfirmDialog(this, panel, "Add New Task", JOptionPane.OK_CANCEL_OPTION);

        if (result == JOptionPane.OK_OPTION) {
            try {
                Task newTask = new Task(
                        descriptionField.getText(),
                        (Integer) prioritySpinner.getValue(),
                        categoryField.getText(),
                        LocalDate.parse(dueDateField.getText(), dateFormatter),
                        recurrenceField.getText()
                );
                taskList.addTask(newTask);
                updateTaskList();
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Invalid input! Please check your data.", "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void showModifyTaskDialog() {
        int selectedIndex = taskJList.getSelectedIndex();
        if (selectedIndex == -1) {
            JOptionPane.showMessageDialog(this, "Please select a task to modify", "No Task Selected", JOptionPane.WARNING_MESSAGE);
            return;
        }

        String selectedTask = listModel.getElementAt(selectedIndex);
        String oldDescription = selectedTask.split("\\(")[0].substring(2).trim();

        Task current = taskList.getHead();
        Task original = null;
        while (current != null) {
            if (current.description.equalsIgnoreCase(oldDescription)) {
                original = current;
                break;
            }
            current = current.next;
        }

        if (original == null) return;

        JPanel panel = new JPanel(new GridLayout(5, 2, 5, 5));

        JTextField descriptionField = new JTextField(original.description);
        JSpinner prioritySpinner = new JSpinner(new SpinnerNumberModel(original.priority, 1, 10, 1));
        JTextField categoryField = new JTextField(original.category);
        JTextField dueDateField = new JTextField(original.dueDate.format(dateFormatter));
        JTextField recurrenceField = new JTextField(original.recurrence);

        panel.add(new JLabel("Description:"));
        panel.add(descriptionField);
        panel.add(new JLabel("Priority (1-10):"));
        panel.add(prioritySpinner);
        panel.add(new JLabel("Category:"));
        panel.add(categoryField);
        panel.add(new JLabel("Due Date (dd-MM-yyyy):"));
        panel.add(dueDateField);
        panel.add(new JLabel("Recurrence:"));
        panel.add(recurrenceField);

        int result = JOptionPane.showConfirmDialog(this, panel, "Modify Task", JOptionPane.OK_CANCEL_OPTION);

        if (result == JOptionPane.OK_OPTION) {
            try {
                Task updatedTask = new Task(
                        descriptionField.getText(),
                        (Integer) prioritySpinner.getValue(),
                        categoryField.getText(),
                        LocalDate.parse(dueDateField.getText(), dateFormatter),
                        recurrenceField.getText()
                );

                if (taskList.updateTask(oldDescription, updatedTask)) {
                    updateTaskList();
                }
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Invalid input!", "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void completeSelectedTask() {
        int selectedIndex = taskJList.getSelectedIndex();
        if (selectedIndex != -1) {
            String selectedTask = listModel.getElementAt(selectedIndex);
            String description = selectedTask.split("\\(")[0].substring(2).trim();

            boolean removed = taskList.removeTask(description);
            if (removed) {
                updateTaskList();
                JOptionPane.showMessageDialog(this, "Task '" + description + "' completed and removed.");
            }
        } else {
            JOptionPane.showMessageDialog(this, "Please select a task to complete.", "No Task Selected", JOptionPane.WARNING_MESSAGE);
        }
    }

    private class ButtonClickListener implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            String command = e.getActionCommand();

            switch (command) {
                case "Add Task":
                    showAddTaskDialog();
                    break;
                case "Modify Task":
                    showModifyTaskDialog();
                    break;
                case "Complete Task":
                    completeSelectedTask();
                    break;
                case "Display Tasks":
                    updateTaskList();
                    break;
                case "Reverse Display":
                    updateReversedTaskList();
                    break;
                case "Count Tasks":
                    JOptionPane.showMessageDialog(TaskManagerGUI.this, "Total pending tasks: " + taskList.countTasks());
                    break;
                case "Clear Tasks":
                    int confirm = JOptionPane.showConfirmDialog(TaskManagerGUI.this,
                            "Are you sure you want to clear all tasks?", "Confirm Clear", JOptionPane.YES_NO_OPTION);
                    if (confirm == JOptionPane.YES_OPTION) {
                        taskList.clearTasks();
                        updateTaskList();
                    }
                    break;
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            TaskManagerGUI gui = new TaskManagerGUI();
            gui.setVisible(true);
        });
    }
}
