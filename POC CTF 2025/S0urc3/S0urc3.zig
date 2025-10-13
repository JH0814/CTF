const std = @import("std");

const encoded_flag = [_]u8{ 71,105,102,104,88,120,107,108,49,54,103,55,52,45,104,110,51,98,60,58,52,98,103,106,55,97,105,110,50,96,55,59,99,49,60,61,56,54,130 };

fn decodeFlag(allocator: std.mem.Allocator) ![]u8 {
    var decoded = try allocator.alloc(u8, encoded_flag.len);
    
    for (encoded_flag, 0..) |byte, i| {
        switch (i % 4) {
            0 => decoded[i] = byte ^ 0x01,
            1 => decoded[i] = byte + 3,
            2 => decoded[i] = byte - 5,
            3 => decoded[i] = byte ^ 0x0F,
            else => unreachable,
        }
    }
    
    return decoded;
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    const flag = try decodeFlag(allocator);
    defer allocator.free(flag);
}