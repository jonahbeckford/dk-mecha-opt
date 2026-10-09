namespace MechaDk;

public sealed partial class MainPage : Page
{
    public MainPage()
    {
        this.InitializeComponent();
        NativeTextBlock.Text = NativeMethods.MakeItSo();
    }
}
