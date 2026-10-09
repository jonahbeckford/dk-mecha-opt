using System.Runtime.InteropServices;

namespace MechaDk;

/// <summary>The C function in native/mechadk_native.c, built by CMake (see Native.targets).</summary>
internal static partial class NativeMethods
{
#if __IOS__
    // Static library linked into the app.
    private const string Library = "__Internal";
#elif __WASM__
    // The P/Invoke table names a statically linked module after its file, libmechadk_native.a.
    private const string Library = "libmechadk_native";
#else
    private const string Library = "mechadk_native";
#endif

    [LibraryImport(Library, EntryPoint = "mechadk_make_it_so")]
    private static partial IntPtr MakeItSoPtr();

    /// <summary>The returned pointer is static, so it is read and never freed.</summary>
    public static string MakeItSo() => Marshal.PtrToStringUTF8(MakeItSoPtr()) ?? "";
}
